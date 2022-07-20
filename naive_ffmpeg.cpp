#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <chrono>
#include <iostream>
extern "C" {
#include <libavcodec/avcodec.h>
}

#define INBUF_SIZE 4096

uint64_t get_timestamp() {
    using namespace std::chrono;
    return duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
}

static void decode(AVCodecContext* dec_ctx, AVFrame* frame, AVPacket* pkt)
{
    char buf[1024];
    int ret;
    
    ret = avcodec_send_packet(dec_ctx, pkt);
    if (ret < 0) {
        fprintf(stderr, "Error sending a packet for decoding\n");
        exit(1);
    }

    while (ret >= 0) {
        ret = avcodec_receive_frame(dec_ctx, frame);
        if (ret == AVERROR(EAGAIN) || ret == AVERROR_EOF)
            return;
        else if (ret < 0) {
            fprintf(stderr, "Error during decoding\n");
            exit(1);
        }
        //printf("%d\n",dec_ctx->frame_number);
        //fflush(stdout);
    }
}

int main(int argc, char** argv)
{
    av_log_set_level(AV_LOG_QUIET);
    auto start = get_timestamp();
    const char *filename, *codecname;
    const AVCodec* codec;
    AVCodecParserContext* parser;
    AVCodecContext* c = NULL;
    FILE* f;
    AVFrame* frame;
    uint8_t inbuf[INBUF_SIZE + AV_INPUT_BUFFER_PADDING_SIZE];
    uint8_t* data;
    size_t   data_size;
    int ret;
    int eof;
    int num_threads;
    AVPacket* pkt;

    /* TODO add proper parsing of inputs*/
    if (argc <= 3) {
        fprintf(stderr, "Usage: %s <input file> <codec> num_threads\n", argv[0]);
        exit(0);
    }
    filename    = argv[1];
    codecname   = argv[2];
    num_threads = atoi(argv[3]);

    pkt = av_packet_alloc();
    if (!pkt)
        exit(1);

    /* set end of buffer to 0 (this ensures that no overreading happens for damaged MPEG streams) */
    memset(inbuf + INBUF_SIZE, 0, AV_INPUT_BUFFER_PADDING_SIZE);

    codec = avcodec_find_decoder_by_name(codecname);
    
    if (!codec) {
        fprintf(stderr, "Codec not found\n");
        exit(1);
    }

    parser = av_parser_init(codec->id);
    if (!parser) {
        fprintf(stderr, "parser not found\n");
        exit(1);
    }

    c = avcodec_alloc_context3(codec);
    if (!c) {
        fprintf(stderr, "Could not allocate video codec context\n");
        exit(1);
    }
    
    c->thread_count = num_threads;

    if (avcodec_open2(c, codec, NULL) < 0) {
        fprintf(stderr, "Could not open codec\n");
        exit(1);
    }

    f = fopen(filename, "rb");
    if (!f) {
        fprintf(stderr, "Could not open %s\n", filename);
        exit(1);
    }

    frame = av_frame_alloc();
    if (!frame) {
        fprintf(stderr, "Could not allocate video frame\n");
        exit(1);
    }

    while (!feof(f)) {
        /* read raw data from the input file */
        data_size = fread(inbuf, 1, INBUF_SIZE, f);
        if (!data_size)
            break;
        /* use the parser to split the data into frames */
        data = inbuf;
        while (data_size > 0) {
            ret = av_parser_parse2(parser, c, &pkt->data, &pkt->size,
                                   data, data_size, AV_NOPTS_VALUE, AV_NOPTS_VALUE, 0);
            if (ret < 0) {
                fprintf(stderr, "Error while parsing\n");
                exit(1);
            }
            data      += ret;
            data_size -= ret;
            if (pkt->size)
                decode(c, frame, pkt);
        }
    }

    /* flush the decoder */
    decode(c, frame, NULL);
    
    int frames_tot = c->frame_number;

    fclose(f);

    av_parser_close(parser);
    avcodec_free_context(&c);
    av_frame_free(&frame);
    av_packet_free(&pkt);

    auto end = get_timestamp();
    double duration = (end - start)/1000.0;
    double fps = frames_tot/duration;

    std::cout << "Frame number: " << frames_tot 
              << ", Time elapsed: " << duration
              << "s, FPS: " << fps 
              << std::endl;
    return 0;
}
