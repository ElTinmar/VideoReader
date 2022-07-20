# Optimize machine vision processing of video files

TL/DR

- Matlab VideoReader is slowish but not that bad
- Using single vs double precision images may be faster
- Using a multiprocessed producer-consumer scheme instead of the naive sequential read-process approach can yield significant improvements 
in overall speed if the processing task is long and not already multithreaded. 
- For short processing tasks, the overhead introduced by the multiprocessing approach results in no clear benefits or even worse performance than the sequential approach 
- If the task is already multithreaded (e.g. SVD from openBLAS), using several consumer thread processes can be worse
- If the task is already multithreaded (e.g. SVD from openBLAS), reducing OMP_NUM_THREADS (controls the number of parallel threads for openBLAS) and increasing the number of consumers may increase performance
- When processing is slow, using hardware acceleration to decode frames from the video file can free up CPU resources. If the producer queue gets 
full quickly, there may be an initial speed up, but the producer won't be using many CPU cycles anyway
- TO TEST Running the consumer processing code on the GPU when possible can yield a significant speed-up 
- TO TEST You may need parallel producers (read several video chunks at the same time) if you are doing some very light processing (e.g. just counting the number of frames)
- TO TEST Hyperthreading ? On hyperthreaded processors, it looks like peak performance is reached for OMP_NUM_THREADS = num physical cores. Popular wisdom tends to advise against hyperthreading

General advice

- Keep an eye on `top` or `htop` to see if all cores are in use
- Keep an eye on the size of the producer queue 

<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:xlink="http://www.w3.org/1999/xlink"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="180.20351mm"
   height="34.820499mm"
   viewBox="0 0 180.20351 34.820499"
   version="1.1"
   id="svg8"
   inkscape:version="0.92.5 (2060ec1f9f, 2020-04-08)"
   sodipodi:docname="producer_consumer.svg">
  <defs
     id="defs2">
    <marker
       inkscape:stockid="Arrow1Lend"
       orient="auto"
       refY="0"
       refX="0"
       id="Arrow1Lend"
       style="overflow:visible"
       inkscape:isstock="true">
      <path
         id="path4773"
         d="M 0,0 5,-5 -12.5,0 5,5 Z"
         style="fill:#000000;fill-opacity:1;fill-rule:evenodd;stroke:#000000;stroke-width:1.00000003pt;stroke-opacity:1"
         transform="matrix(-0.8,0,0,-0.8,-10,0)"
         inkscape:connector-curvature="0" />
    </marker>
  </defs>
  <sodipodi:namedview
     id="base"
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1.0"
     inkscape:pageopacity="0.0"
     inkscape:pageshadow="2"
     inkscape:zoom="2.8"
     inkscape:cx="219.5782"
     inkscape:cy="-202.80934"
     inkscape:document-units="mm"
     inkscape:current-layer="layer1"
     showgrid="false"
     fit-margin-top="0"
     fit-margin-left="0"
     fit-margin-right="0"
     fit-margin-bottom="0"
     inkscape:window-width="4976"
     inkscape:window-height="2752"
     inkscape:window-x="144"
     inkscape:window-y="54"
     inkscape:window-maximized="1" />
  <metadata
     id="metadata5">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <g
     inkscape:label="Layer 1"
     inkscape:groupmode="layer"
     id="layer1"
     transform="translate(-12.674173,-23.110141)">
    <g
       id="g5538">
      <g
         transform="rotate(-90,60.637127,52.895922)"
         id="g5320">
        <g
           id="g825"
           transform="matrix(0.134674,0,0,0.134674,64.360282,21.564553)"
           inkscape:tile-cx="88.221327"
           inkscape:tile-cy="29.571793"
           inkscape:tile-w="4.4031581"
           inkscape:tile-h="7.5885387"
           inkscape:tile-x0="86.019748"
           inkscape:tile-y0="25.777524">
          <rect
             style="fill:#ffcc00;fill-opacity:1;stroke:none;stroke-width:0.1984375;stroke-miterlimit:10;stroke-dasharray:none;stroke-dashoffset:0"
             id="rect819"
             width="32.694939"
             height="16.347469"
             x="160.82887"
             y="31.282736" />
          <rect
             y="47.630203"
             x="160.82887"
             height="40"
             width="32.694939"
             id="rect821"
             style="fill:#0066ff;fill-opacity:1;stroke:none;stroke-width:0.31040484;stroke-miterlimit:10;stroke-dasharray:none;stroke-dashoffset:0" />
        </g>
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           id="use4580" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,7.5885387)"
           id="use4582" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,15.177077)"
           id="use4584" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,22.765616)"
           id="use4586" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,30.354155)"
           id="use4588" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,37.942693)"
           id="use4590" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,45.531232)"
           id="use4592" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,53.119771)"
           id="use4594" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,60.708309)"
           id="use4596" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,68.296848)"
           id="use4598" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,75.885387)"
           id="use4600" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,83.473925)"
           id="use4602" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,91.062464)"
           id="use4604" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,98.651002)"
           id="use4606" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,106.23954)"
           id="use4608" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,113.82808)"
           id="use4610" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,121.41662)"
           id="use4612" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,129.00516)"
           id="use4614" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,136.5937)"
           id="use4616" />
        <use
           height="100%"
           width="100%"
           x="0"
           y="0"
           inkscape:tiled-clone-of="#g825"
           xlink:href="#g825"
           transform="translate(0,144.18223)"
           id="use4618" />
      </g>
      <g
         transform="rotate(-90,78.987841,71.246637)"
         id="g5277">
        <g
           id="g4723"
           transform="translate(-5.8208336)">
          <rect
             inkscape:tile-y0="25.777524"
             inkscape:tile-x0="113.09097"
             inkscape:tile-h="2.201579"
             inkscape:tile-w="4.4031581"
             inkscape:tile-cy="26.878314"
             inkscape:tile-cx="115.29255"
             y="25.777525"
             x="113.09097"
             height="2.2015791"
             width="4.4031582"
             id="rect827"
             style="fill:#ffcc00;fill-opacity:1;stroke:none;stroke-width:0.02672437;stroke-miterlimit:10;stroke-dasharray:none;stroke-dashoffset:0" />
          <use
             id="use4622"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4624"
             transform="translate(0,2.201579)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4626"
             transform="translate(0,4.4031581)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4628"
             transform="translate(0,6.6047371)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4630"
             transform="translate(0,8.8063162)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4632"
             transform="translate(0,11.007895)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4634"
             transform="translate(0,13.209474)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4636"
             transform="translate(0,15.411053)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4638"
             transform="translate(0,17.612632)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4640"
             transform="translate(0,19.814211)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4642"
             transform="translate(0,22.01579)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4644"
             transform="translate(0,24.217369)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4646"
             transform="translate(0,26.418949)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4648"
             transform="translate(0,28.620528)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4650"
             transform="translate(0,30.822107)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4652"
             transform="translate(0,33.023686)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4654"
             transform="translate(0,35.225265)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4656"
             transform="translate(0,37.426844)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4658"
             transform="translate(0,39.628423)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4660"
             transform="translate(0,41.830002)"
             xlink:href="#rect827"
             inkscape:tiled-clone-of="#rect827"
             y="0"
             x="0"
             width="100%"
             height="100%" />
        </g>
        <g
           id="g4746"
           transform="translate(-10.772578)">
          <rect
             inkscape:tile-y0="25.777524"
             inkscape:tile-x0="122.44587"
             inkscape:tile-h="5.3869599"
             inkscape:tile-w="4.4031581"
             inkscape:tile-cy="28.471004"
             inkscape:tile-cx="124.64745"
             style="fill:#0066ff;fill-opacity:1;stroke:none;stroke-width:0.04180346;stroke-miterlimit:10;stroke-dasharray:none;stroke-dashoffset:0"
             id="rect829"
             width="4.4031582"
             height="5.38696"
             x="122.44588"
             y="25.777525" />
          <use
             id="use4662"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4664"
             transform="translate(0,5.3869599)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4666"
             transform="translate(0,10.77392)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4668"
             transform="translate(0,16.16088)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4670"
             transform="translate(0,21.54784)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4672"
             transform="translate(0,26.9348)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4674"
             transform="translate(0,32.321759)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4676"
             transform="translate(0,37.708719)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4678"
             transform="translate(0,43.095679)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4680"
             transform="translate(0,48.482639)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4682"
             transform="translate(0,53.869599)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4684"
             transform="translate(0,59.256559)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4686"
             transform="translate(0,64.643519)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4688"
             transform="translate(0,70.030479)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4690"
             transform="translate(0,75.417439)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4692"
             transform="translate(0,80.804399)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4694"
             transform="translate(0,86.191358)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4696"
             transform="translate(0,91.578318)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4698"
             transform="translate(0,96.965278)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
          <use
             id="use4700"
             transform="translate(0,102.35224)"
             xlink:href="#rect829"
             inkscape:tiled-clone-of="#rect829"
             y="0"
             x="0"
             width="100%"
             height="100%" />
        </g>
      </g>
      <text
         id="text4750"
         y="26.553677"
         x="20.817816"
         style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-size:3.52777767px;line-height:10;font-family:Arial;-inkscape-font-specification:'Arial Bold';letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.26458332"
         xml:space="preserve"><tspan
           style="stroke-width:0.26458332"
           y="26.553677"
           x="20.817816"
           id="tspan4748"
           sodipodi:role="line">naive</tspan></text>
      <g
         transform="translate(-92.793403,25.283643)"
         id="g5231">
        <text
           id="text4754"
           y="12.667412"
           x="106.06013"
           style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-size:3.52777767px;line-height:10;font-family:Arial;-inkscape-font-specification:'Arial Bold';letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.26458332"
           xml:space="preserve"><tspan
             style="stroke-width:0.26458332"
             y="12.667412"
             x="106.06013"
             id="tspan4752"
             sodipodi:role="line">producer</tspan><tspan
             style="stroke-width:0.26458332"
             y="47.94519"
             x="106.06013"
             sodipodi:role="line"
             id="tspan4756" /></text>
        <text
           xml:space="preserve"
           style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-size:3.52777767px;line-height:10;font-family:Arial;-inkscape-font-specification:'Arial Bold';letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.26458332"
           x="105.32116"
           y="16.371576"
           id="text4762"><tspan
             id="tspan4760"
             sodipodi:role="line"
             x="105.32116"
             y="16.371576"
             style="stroke-width:0.26458332">consumer</tspan></text>
      </g>
      <path
         inkscape:connector-curvature="0"
         id="path4768"
         d="M 33.518729,51.810633 H 192.36322"
         style="fill:none;stroke:#000000;stroke-width:0.26499999;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1;marker-end:url(#Arrow1Lend)" />
      <g
         id="g5452"
         transform="translate(79.374752,45.221887)">
        <text
           xml:space="preserve"
           style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-size:3.52777767px;line-height:10;font-family:Arial;-inkscape-font-specification:'Arial Bold';letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.26458332"
           x="106.06013"
           y="12.667412"
           id="text5446"><tspan
             sodipodi:role="line"
             id="tspan5442"
             x="106.06013"
             y="12.667412"
             style="stroke-width:0.26458332">time</tspan><tspan
             id="tspan5444"
             sodipodi:role="line"
             x="106.06013"
             y="47.94519"
             style="stroke-width:0.26458332" /></text>
        <text
           id="text5450"
           y="16.371576"
           x="105.32116"
           style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-size:3.52777767px;line-height:10;font-family:Arial;-inkscape-font-specification:'Arial Bold';letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.26458332"
           xml:space="preserve"><tspan
             style="stroke-width:0.26458332"
             y="34.983265"
             x="105.32116"
             sodipodi:role="line"
             id="tspan5448" /></text>
      </g>
    </g>
  </g>
</svg>

## download test video 

```
$ sudo pip install youtube-dl
$ youtube-dl --format "best[ext=mp4][protocol=https]" https://www.youtube.com/watch?v=9eiaiVthVrk -o jumanji.mp4
ffmpeg -ss 00 -i jumanji.mp4 -c copy -t 04 jumanji_short.mp4
```

## Naive processing of images

In Matlab

``` matlab
mov = VideoReader('jumanji.mp4');
num_frame = 0;
while mov.hasFrame()
    frame = mov.readFrame();
    frame_gray = frame(:,:,1);
    num_frame = num_frame+1;
    
    pause(0.1);
    disp(num_frame);
end
```

In Python

``` python
import os
import cv2
import time 

use_gpu = False

# Hardware acceleration on NVIDIA GPU if FFMPEG was compiled with CUVID support
if use_gpu:
	os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]="video_codec;h264_cuvid"
	
cap = cv2.VideoCapture("jumanji.mp4", cv2.CAP_FFMPEG)
frame_num = 0

def process(frame,frame_num):	
    # simulate long processing
    time.sleep(0.1)
    print(frame_num)

while True:
    # Get frames here
    rval, frame = cap.read()
    if not rval:
        break
    
    frame_gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
    frame_num += 1
    
    process(frame_gray,frame_num)

cap.release()
```

In C/C++ with ffmpeg

```cpp
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>
extern "C" {
#include <libavcodec/avcodec.h>
}

#define INBUF_SIZE 4096

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
        printf("%d\n",dec_ctx->frame_number);
        fflush(stdout);
    }
}

int main(int argc, char** argv)
{
    av_log_set_level(AV_LOG_QUIET);
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
    int num_threads = 1;
    AVPacket* pkt;

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

    fclose(f);

    av_parser_close(parser);
    avcodec_free_context(&c);
    av_frame_free(&frame);
    av_packet_free(&pkt);

    return 0;
}
```

compile with 

```
g++ naive_ffmpeg.cpp \
-I/home/martin/ffmpeg_build/include \
-L/home/martin/ffmpeg_build/lib \
-lavformat \
-lavcodec \
-lavutil \
-lavdevice \
-lavfilter \
-o naive_ffmpeg
```

## Multiprocessing producer-consumer scheme

``` python
from multiprocessing import Process, Queue, JoinableQueue
import cv2
import time
import os
import queue

def producer(path, use_gpu, frame_queue):
    """get images from file and put them in a queue"""

    if use_gpu:
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]="video_codec;h264_cuvid"

    stream = cv2.VideoCapture(path)
    frame_num = 0
        
    while True:
        grabbed, frame = stream.read()
        if not grabbed:
            break
                
        frame_gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)        
        frame_num += 1
        frame_queue.put((frame_gray, frame_num))
        
    stream.release()
    # Wait until queue is emptied by consumers 
    frame_queue.join()

def consumer(frame_queue, result_queue, process_num, process_fun):
    """process images from the queue """

    while True: 
        try:
            # get frame and frame number from the queue
            frame, frame_num = frame_queue.get(block=False)                                                                                                             
            # do some processing
            process_fun(frame,frame_num,frame_queue,result_queue)
            
            frame_queue.task_done()
            
        except queue.Empty:
            pass
        
def start(frame_queue, result_queue, videofile, n_consumers=1, use_gpu=False):
    """spawn all the processes"""

    # start consumers and producers                                             
    consumer_process = [];                                                      
    for i in range(n_consumers):                                                
        p = Process(
            target=consumer, 
            args=(frame_queue, result_queue, i, process,),
            daemon=True) # allow consumers to be closed when queue is empty
        consumer_process.append(p)                                              
        p.start()

    producer_process = Process(target=producer, 
                        args=(videofile,use_gpu,frame_queue,))    
    producer_process.start()

    # wait for producers to terminate                             
    producer_process.join()

def process(frame,frame_num,frame_queue,result_queue):
    """actual image processing code goes here"""
    
    # simulate long processing task
    time.sleep(0.1)
    print((frame_queue.qsize(), frame_num))

if __name__ == "__main__":
    
    # set parameters
    frame_queue = JoinableQueue(maxsize = 2048)
    result_queue = Queue()
    videofile = '/home/martin/jumanji.mp4'
    n_consumers = 1

    start(frame_queue, result_queue, videofile, n_consumers, use_gpu=False)
```

## Results

Hardware:  
Intel(R) Core(TM) i5-2500S CPU @ 2.70GHz (4 cores, 4 threads)   
Intel® HD Graphics 2000   
12 GB of 1333 MHz DDR3   

### Using time.sleep as a synthetic load (not CPU intensive)

| Command | Wait duration | #Consumers | Hardware acceleration | Real time |
| --- | --- | --- | --- | --- |
| matlab -nodesktop -r "tic; run('naive.m'); toc; exit;" | 100 ms | NA | No | 7m06,613s |
| time python3 naive.py | 100 ms | NA | No | 6m47,355s |
| time python3 producer_consumer.py | 100 ms | 1 | No | 6m46,246s |
| time python3 producer_consumer.py | 100 ms | 2 | No | 3m23,020s |
| time python3 producer_consumer.py | 100 ms | 3 | No | 2m15,463s |
| time python3 producer_consumer.py | 100 ms | 4 | No | 1m41,924s |
| time python3 producer_consumer.py | 100 ms | 5 | No | 1m21,792s |
| time python3 producer_consumer.py | 100 ms | 10 | No | 0m43,272s |
| time python3 producer_consumer.py | 100 ms | 15 | No | 0m38,774s :heavy_check_mark: |
| time python3 producer_consumer.py | 100 ms | 20 | No | 1m9,684s |
| time python3 naive.py | 10 ms | NA | No | 0m52,553s |
| time python3 producer_consumer.py | 10 ms | 1 | No | 0m51,554s |
| time python3 producer_consumer.py | 10 ms | 2 | No | 0m29,503s |
| time python3 producer_consumer.py | 10 ms | 5 | No | 0m28,546s :heavy_check_mark: |
| time python3 producer_consumer.py | 10 ms | 10 | No | 0m48,809s |
| time python3 naive.py | 1 ms | NA | No | 0m19,729s |
| time python3 producer_consumer.py | 1 ms | 1 | No | 0m24,054s :skull: |
| time python3 producer_consumer.py | 1 ms | 2 | No | 0m22,645s :skull: |
| time python3 producer_consumer.py | 1 ms | 3 | No | 0m26,689s :skull: |


### Using busy_wait as a synthetic load (CPU intensive, single core)

``` python
def busy_wait(dt):   
    current_time = time.time()
    while (time.time() < current_time+dt):
        pass

def process(frame,frame_num):
    """actual image processing code goes here"""
    
    busy_wait(0.1)
    print(frame_num)
```


| Command | Wait duration | #Consumers | Hardware acceleration | Real time |
| --- | --- | --- | --- | --- |
| time python3 naive.py | 100 ms | NA | No | 6m42,774s :skull: |
| time python3 producer_consumer.py | 100 ms | 1 | No | 6m42,629s |
| time python3 producer_consumer.py | 100 ms | 2 | No | 3m24,008s |
| time python3 producer_consumer.py | 100 ms | 5 | No | 1m29,378s |
| time python3 producer_consumer.py | 100 ms | 10 | No | 0m56,405s :heavy_check_mark: |
| time python3 producer_consumer.py | 100 ms | 15 | No | 1m11,180s |

### Using SVD as a synthetic load (CPU intensive, multicore)

Make sure that numpy is using a multi-threaded BLAS library such as openBLAS. On ubuntu

```
sudo apt install libopenblas-base libopenblas-dev
```

``` python
import numpy as np

def process(frame,frame_num):
    """actual image processing code goes here"""
    
    frame32 = np.float32(frame)                                                 
    u, s, vh = np.linalg.svd(frame32)
    print(frame_num)
```

| Command | #Consumers | Hardware acceleration | Real time |
| --- | --- | --- | --- |
| time python3 naive.py | NA | No | 37m22,286s |
| time python3 producer_consumer.py | 1 | No | 37m36,874s |
| time python3 producer_consumer.py | 5 | No | 55m59,641s :skull: |

Hardware:  
2x Intel(R) Xeon(R) Gold 5220 CPU @ 2.20GHz (36 cores, 72 threads)  
NVIDIA GeForce RTX 2080 Ti  
64GB (4x16GB) DDR4 2933 MHz  

| Command | Method | Wait duration | #Consumers | Hardware acceleration | Real time | Comments |
| --- | --- | --- | --- | --- | --- | --- |
| time python3 naive.py | time.sleep | 100 ms | NA | No | 6m48,654s | |
| time python3 producer_consumer.py | time.sleep | 100 ms | 15 | No | 0m28,396s | |
| time python3 producer_consumer.py | time.sleep | 100 ms | 30 | No | 0m15,574s | |
| time python3 producer_consumer.py | time.sleep | 100 ms | 60 | No | 0m13,529s | |
| time python3 producer_consumer.py | time.sleep | 100 ms | 100 | No | 2m9,737s | |
| time python3 naive.py | SVD | NA | NA | No | 9m21,224s | openBLAS is using 36 cores |
| OMP_NUM_THREADS=1 time python3 naive.py | SVD | NA | NA | No | 22m54,347s |  |
| OMP_NUM_THREADS=5 time python3 naive.py | SVD | NA | NA | No | 7m47,355s |  |
| OMP_NUM_THREADS=10 time python3 naive.py | SVD | NA | NA | No | 7m27,554s |  |
| OMP_NUM_THREADS=15 time python3 naive.py | SVD | NA | NA | No | 7m33,004s |  |
| OMP_NUM_THREADS=25 time python3 naive.py | SVD | NA | NA | No | 9m27,125s |  |
| OMP_NUM_THREADS=36 time python3 naive.py | SVD | NA | NA | No | 9m37,050s |  |
| time python3 producer_consumer.py | SVD | NA | 1 | No | x | |
| time python3 producer_consumer.py | SVD | NA | 2 | No | 5m45,433s | |
| OMP_NUM_THREADS=1 time python3 producer_consumer.py | SVD | NA | 40 | No | 4m3,459s | |
| OMP_NUM_THREADS=5 time python3 producer_consumer.py | SVD | NA | 10 | No | 1m37,042s | |
| OMP_NUM_THREADS=5 time python3 producer_consumer.py | SVD | NA | 12 | No | 1m31,409s | |


Hardware:                                                                       
2x Intel(R) Xeon(R) CPU X5667 @3.07GHz (8 cores, 16 threads)         
NVIDIA GeForce RTX 3050                                                      
96GB (4x16GB + 8x4GB) DDR3 1333 MHz  

| Command | Method | Wait duration | #Consumers | Hardware acceleration | Real time | Comments |
| --- | --- | --- | --- | --- | --- | --- |
| OMP_NUM_THREADS=2 time python3 producer_consumer.py | SVD | NA | 6 | No | 15m4,216s |  |
| OMP_NUM_THREADS=2 time python3 producer_consumer.py | SVD | NA | 6 | Yes | 15m10,400s |  |

OMP_NUM_THREADS=1 ./naive.py ../jumanji_short.mp4 --gpu : 96.53809785842896
OMP_NUM_THREADS=1 ./naive.py ../jumanji_short.mp4 : 87.77525496482849
OMP_NUM_THREADS=2 ./naive.py ../jumanji_short.mp4 --gpu : 62.90791964530945
OMP_NUM_THREADS=2 ./naive.py ../jumanji_short.mp4 : 60.695536851882935
OMP_NUM_THREADS=3 ./naive.py ../jumanji_short.mp4 --gpu : 48.07580018043518
OMP_NUM_THREADS=3 ./naive.py ../jumanji_short.mp4 : 51.99619936943054
OMP_NUM_THREADS=4 ./naive.py ../jumanji_short.mp4 --gpu : 43.058756828308105
OMP_NUM_THREADS=4 ./naive.py ../jumanji_short.mp4 : 41.928311824798584
OMP_NUM_THREADS=5 ./naive.py ../jumanji_short.mp4 --gpu : 41.51391625404358
OMP_NUM_THREADS=5 ./naive.py ../jumanji_short.mp4 : 42.57131266593933
OMP_NUM_THREADS=6 ./naive.py ../jumanji_short.mp4 --gpu : 39.16380214691162
OMP_NUM_THREADS=6 ./naive.py ../jumanji_short.mp4 : 40.0044310092926
OMP_NUM_THREADS=7 ./naive.py ../jumanji_short.mp4 --gpu : 37.68110918998718
OMP_NUM_THREADS=7 ./naive.py ../jumanji_short.mp4 : 38.56710171699524
OMP_NUM_THREADS=8 ./naive.py ../jumanji_short.mp4 --gpu : 34.84391903877258
OMP_NUM_THREADS=8 ./naive.py ../jumanji_short.mp4 : 36.19422149658203
OMP_NUM_THREADS=9 ./naive.py ../jumanji_short.mp4 --gpu : 39.161625385284424
OMP_NUM_THREADS=9 ./naive.py ../jumanji_short.mp4 : 43.20840048789978
OMP_NUM_THREADS=10 ./naive.py ../jumanji_short.mp4 --gpu : 40.219749450683594
OMP_NUM_THREADS=10 ./naive.py ../jumanji_short.mp4 : 41.39073467254639
OMP_NUM_THREADS=11 ./naive.py ../jumanji_short.mp4 --gpu : 41.889657974243164
OMP_NUM_THREADS=11 ./naive.py ../jumanji_short.mp4 : 43.51589894294739
OMP_NUM_THREADS=12 ./naive.py ../jumanji_short.mp4 --gpu : 37.1433527469635
OMP_NUM_THREADS=12 ./naive.py ../jumanji_short.mp4 : 40.55977511405945
OMP_NUM_THREADS=13 ./naive.py ../jumanji_short.mp4 --gpu : 41.36651873588562
OMP_NUM_THREADS=13 ./naive.py ../jumanji_short.mp4 : 41.3347532749176
OMP_NUM_THREADS=14 ./naive.py ../jumanji_short.mp4 --gpu : 38.32852816581726
OMP_NUM_THREADS=14 ./naive.py ../jumanji_short.mp4 : 43.07148814201355
OMP_NUM_THREADS=15 ./naive.py ../jumanji_short.mp4 --gpu : 42.21801280975342
OMP_NUM_THREADS=15 ./naive.py ../jumanji_short.mp4 : 42.88045406341553
OMP_NUM_THREADS=16 ./naive.py ../jumanji_short.mp4 --gpu : 43.762839555740356
OMP_NUM_THREADS=16 ./naive.py ../jumanji_short.mp4 : 45.965179443359375
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 88.21587181091309
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 1 : 87.82719278335571
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 60.34035539627075
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 1 : 60.97363805770874
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 51.416282653808594
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 1 : 52.030717611312866
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 43.99580454826355
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 1 : 42.302817821502686
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 41.950417041778564
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 1 : 42.346333742141724
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 40.1317093372345
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 1 : 38.958621978759766
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 38.4332435131073
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 1 : 38.54747772216797
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 36.67916178703308
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 1 : 36.41473317146301
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 44.92967772483826
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 1 : 42.7352876663208
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 45.233720541000366
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 1 : 41.21193528175354
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 42.30559325218201
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 1 : 44.06795263290405
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 43.51270580291748
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 1 : 40.86403036117554
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 42.7571485042572
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 1 : 41.34889483451843
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 43.18969249725342
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 1 : 42.82621741294861
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 44.214465379714966
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 1 : 43.29290699958801
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 1--gpu : 45.72227644920349
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 1 : 45.85324692726135
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 44.969006061553955
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 2 : 44.86065983772278
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 28.155245065689087
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 2 : 32.01388764381409
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 27.89858889579773
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 2 : 24.642163515090942
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 24.409666538238525
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 2 : 21.64210319519043
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 33.199503898620605
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 2 : 30.48926830291748
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 29.390370845794678
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 2 : 30.0242760181427
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 28.895533561706543
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 2 : 27.9451801776886
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 28.747238874435425
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 2 : 29.671552419662476
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 38.92139148712158
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 2 : 37.918365240097046
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 41.41587448120117
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 2 : 42.35620188713074
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 44.00817155838013
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 2 : 41.731536626815796
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 46.065099000930786
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 2 : 45.65549182891846
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 47.65837240219116
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 2 : 47.87151575088501
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 47.383934020996094
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 2 : 46.98462224006653
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 50.864726066589355
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 2 : 50.03839302062988
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 2--gpu : 54.477057456970215
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 2 : 53.73039960861206
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 32.82949256896973
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 3 : 32.36945676803589
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 22.065921545028687
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 3 : 21.5668363571167
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 25.43062996864319
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 3 : 25.489306688308716
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 26.416190147399902
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 3 : 24.225468397140503
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 25.14372944831848
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 3 : 25.714062929153442
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 33.1015191078186
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 3 : 33.116745471954346
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 38.414950132369995
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 3 : 38.13662838935852
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 37.4961359500885
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 3 : 36.20303773880005
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 39.91320037841797
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 3 : 38.11677312850952
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 41.34499454498291
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 3 : 41.51736497879028
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 46.68614935874939
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 3 : 44.51438355445862
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 51.09594917297363
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 3 : 50.4789183139801
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 51.15861773490906
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 3 : 53.18048691749573
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 54.05003333091736
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 3 : 52.68682026863098
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 56.631025314331055
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 3 : 54.41065692901611
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 3--gpu : 58.97185492515564
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 3 : 58.97029113769531
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 26.545973539352417
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 4 : 24.947633028030396
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 18.51349401473999
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 4 : 17.520984411239624
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 25.45653748512268
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 4 : 25.062609672546387
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 23.50912308692932
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 4 : 26.024126529693604
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 34.1903555393219
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 4 : 32.735735177993774
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 37.25028610229492
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 4 : 36.00957441329956
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 38.74437737464905
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 4 : 34.68246388435364
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 41.270636558532715
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 4 : 37.66656160354614
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 45.24364352226257
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 4 : 42.89241409301758
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 46.55667304992676
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 4 : 44.43893623352051
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 48.129141330718994
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 4 : 47.14695644378662
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 50.237271785736084
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 4 : 49.27503252029419
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 51.48345351219177
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 4 : 53.611111879348755
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 54.71309566497803
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 4 : 53.24131155014038
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 56.973644495010376
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 4 : 56.57623815536499
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 4--gpu : 61.210572242736816
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 4 : 61.81040549278259
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 24.94988179206848
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 5 : 23.609851121902466
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 23.9730863571167
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 5 : 20.052703857421875
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 24.000062942504883
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 5 : 23.259806156158447
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 30.286079168319702
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 5 : 29.51435923576355
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 36.5056893825531
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 5 : 35.00465369224548
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 38.749507665634155
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 5 : 38.83114671707153
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 43.07530617713928
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 5 : 39.50985670089722
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 43.249171018600464
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 5 : 43.18447709083557
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 43.85809588432312
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 5 : 43.944414138793945
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 47.17982578277588
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 5 : 46.93717288970947
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 48.98220157623291
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 5 : 48.11398005485535
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 53.420321464538574
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 5 : 51.955297231674194
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 52.79914855957031
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 5 : 54.703864336013794
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 58.299466133117676
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 5 : 57.20558214187622
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 60.3515408039093
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 5 : 57.98336935043335
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 5--gpu : 61.49346899986267
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 5 : 60.74342346191406
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 22.823013067245483
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 6 : 24.3304660320282
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 21.66060161590576
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 6 : 21.911392211914062
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 25.775858640670776
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 6 : 26.7201030254364
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 30.925909519195557
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 6 : 30.922683000564575
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 36.31629538536072
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 6 : 35.07952165603638
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 40.24360108375549
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 6 : 39.59877133369446
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 42.666860580444336
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 6 : 43.40550374984741
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 45.35449695587158
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 6 : 44.59180951118469
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 46.586997509002686
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 6 : 41.41705012321472
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 48.22242856025696
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 6 : 48.85885286331177
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 52.225985288619995
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 6 : 52.5501012802124
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 52.801764488220215
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 6 : 53.43267893791199
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 55.47020673751831
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 6 : 54.387118101119995
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 55.12731051445007
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 6 : 57.823050022125244
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 58.93438696861267
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 6 : 57.62602162361145
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 6--gpu : 70.71012806892395
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 6 : 68.35651803016663
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 23.305392503738403
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 7 : 24.126367807388306
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 24.3586208820343
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 7 : 25.373137712478638
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 31.000795602798462
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 7 : 28.564324855804443
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 32.481889963150024
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 7 : 32.79117202758789
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 40.34539175033569
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 7 : 38.86792182922363
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 41.215670347213745
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 7 : 40.7005877494812
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 43.165024518966675
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 7 : 42.36615228652954
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 46.5545814037323
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 7 : 45.34117770195007
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 46.36373019218445
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 7 : 47.266326665878296
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 50.00890636444092
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 7 : 50.20349669456482
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 51.806551933288574
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 7 : 51.64041495323181
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 54.8147759437561
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 7 : 54.65032124519348
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 56.17161536216736
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 7 : 55.88523030281067
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 58.96293783187866
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 7 : 58.83993220329285
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 61.65571689605713
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 7 : 61.43395805358887
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 7--gpu : 64.66469359397888
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 7 : 65.97582221031189
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 24.324418783187866
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 8 : 24.28787922859192
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 24.334219217300415
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 8 : 24.758363246917725
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 28.80001211166382
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 8 : 30.39436149597168
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 33.67858839035034
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 8 : 32.71985077857971
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 38.34499716758728
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 8 : 37.21305465698242
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 41.439879417419434
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 8 : 41.537386655807495
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 44.11071038246155
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 8 : 43.14985537528992
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 45.37762093544006
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 8 : 44.581589221954346
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 48.21031212806702
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 8 : 47.67892670631409
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 50.31571435928345
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 8 : 48.6594717502594
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 54.47617149353027
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 8 : 52.5244083404541
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 53.735602140426636
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 8 : 54.035181283950806
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 57.22071623802185
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 8 : 59.46490716934204
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 60.665971755981445
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 8 : 59.918877840042114
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 64.29813838005066
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 8 : 65.67910766601562
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 8--gpu : 64.20638275146484
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 8 : 65.38640022277832
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 24.410809755325317
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 9 : 22.51038932800293
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 24.35063672065735
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 9 : 24.377130031585693
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 31.802990674972534
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 9 : 29.889277935028076
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 36.56202030181885
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 9 : 34.84740233421326
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 40.39493680000305
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 9 : 38.88677787780762
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 43.360589027404785
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 9 : 42.4638397693634
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 44.0081250667572
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 9 : 44.15730094909668
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 47.400251388549805
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 9 : 46.44737148284912
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 48.66189694404602
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 9 : 49.163658142089844
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 51.95113801956177
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 9 : 51.588701009750366
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 56.34156656265259
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 9 : 54.63041353225708
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 55.50443124771118
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 9 : 56.66464567184448
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 60.44650101661682
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 9 : 60.4782350063324
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 64.2400426864624
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 9 : 61.38429117202759
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 63.103086948394775
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 9 : 63.781811475753784
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 9--gpu : 65.46852540969849
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 9 : 66.4932029247284
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 24.520536422729492
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 10 : 24.030486583709717
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 26.212984323501587
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 10 : 24.727521657943726
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 31.944011449813843
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 10 : 31.518474578857422
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 35.308512687683105
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 10 : 35.63726091384888
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 40.44997477531433
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 10 : 42.288636445999146
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 42.84582304954529
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 10 : 43.22926664352417
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 47.01046824455261
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 10 : 45.204540729522705
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 48.16657829284668
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 10 : 47.390695333480835
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 50.1150484085083
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 10 : 50.00694465637207
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 52.58968806266785
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 10 : 52.377368450164795
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 53.79148745536804
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 10 : 54.65626096725464
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 56.06425762176514
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 10 : 57.88567852973938
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 60.031203746795654
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 10 : 59.60515260696411
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 60.70639181137085
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 10 : 64.30568051338196
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 64.27551293373108
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 10 : 63.96896266937256
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 10--gpu : 67.755450963974
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 10 : 67.55714750289917
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 23.273369550704956
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 11 : 23.877700805664062
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 26.584877252578735
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 11 : 25.36853289604187
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 32.55896711349487
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 11 : 32.64407467842102
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 36.07233500480652
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 11 : 36.1114501953125
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 41.9888334274292
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 11 : 40.7198851108551
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 44.40599298477173
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 11 : 43.67232131958008
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 46.81033205986023
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 11 : 45.49135184288025
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 47.42445397377014
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 11 : 48.74792170524597
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 49.9717435836792
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 11 : 50.46543765068054
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 53.40961694717407
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 11 : 53.74202251434326
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 54.765936851501465
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 11 : 55.33207178115845
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 58.22418284416199
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 11 : 57.911967515945435
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 61.17747187614441
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 11 : 60.92775893211365
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 63.15823435783386
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 11 : 63.39773154258728
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 65.95289611816406
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 11 : 65.43675827980042
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 11--gpu : 71.22037959098816
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 11 : 67.08699297904968
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 23.89707326889038
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 12 : 24.20803713798523
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 28.40399718284607
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 12 : 27.46432852745056
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 32.39383673667908
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 12 : 32.96776533126831
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 37.29772448539734
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 12 : 37.25282311439514
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 41.495524168014526
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 12 : 42.08607888221741
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 46.146440505981445
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 12 : 45.11953520774841
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 47.65008187294006
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 12 : 45.39331102371216
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 50.29859256744385
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 12 : 48.041651248931885
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 51.92783999443054
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 12 : 51.44442081451416
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 55.14464545249939
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 12 : 54.111576557159424
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 56.99053335189819
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 12 : 54.287001848220825
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 57.81636023521423
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 12 : 58.67712950706482
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 62.80471181869507
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 12 : 58.87205362319946
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 63.026525020599365
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 12 : 63.85045075416565
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 67.33538389205933
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 12 : 65.55394554138184
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 12--gpu : 68.40835618972778
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 12 : 74.06955075263977
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 24.418545484542847
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 13 : 24.32770586013794
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 27.888301134109497
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 13 : 27.53769278526306
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 33.17829656600952
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 13 : 33.27454328536987
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 37.46096158027649
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 13 : 39.1316819190979
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 41.4478554725647
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 13 : 42.92081809043884
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 45.05768823623657
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 13 : 45.199740171432495
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 46.73912572860718
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 13 : 47.73696708679199
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 48.48920297622681
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 13 : 48.454007387161255
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 75.68375039100647
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 13 : 71.47111964225769
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 54.832605838775635
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 13 : 54.05833911895752
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 58.0939826965332
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 13 : 56.38106918334961
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 58.415525913238525
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 13 : 61.363807916641235
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 61.50048065185547
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 13 : 61.39643597602844
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 66.46444988250732
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 13 : 63.954789876937866
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 72.29652714729309
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 13 : 67.32268738746643
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 13--gpu : 68.60827207565308
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 13 : 70.57672667503357
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 24.787413120269775
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 14 : 24.487128496170044
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 28.97596549987793
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 14 : 27.598352432250977
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 34.57052493095398
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 14 : 33.58784532546997
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 39.27565026283264
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 14 : 37.635244846343994
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 43.24120759963989
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 14 : 43.27672290802002
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 46.967954874038696
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 14 : 45.881048917770386
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 49.566001176834106
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 14 : 47.69779324531555
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 50.49578905105591
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 14 : 49.29255127906799
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 51.3049898147583
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 14 : 52.18573760986328
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 54.57585024833679
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 14 : 54.77580237388611
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 58.03757095336914
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 14 : 56.454819440841675
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 62.26599931716919
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 14 : 59.32405734062195
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 64.62252974510193
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 14 : 62.24689984321594
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 64.98102259635925
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 14 : 63.70421767234802
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 66.63754796981812
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 14 : 71.58729124069214
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 14--gpu : 68.48480248451233
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 14 : 73.08701395988464
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 25.566828727722168
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 15 : 25.789503574371338
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 29.759664297103882
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 15 : 29.193352937698364
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 34.69122910499573
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 15 : 33.218376874923706
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 38.065731048583984
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 15 : 39.54156708717346
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 44.100444316864014
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 15 : 43.8474235534668
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 47.64616346359253
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 15 : 47.59923839569092
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 49.19467806816101
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 15 : 48.27851438522339
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 49.83601689338684
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 15 : 50.34886407852173
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 52.96790838241577
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 15 : 53.45940017700195
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 54.92701816558838
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 15 : 55.26722860336304
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 60.03580641746521
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 15 : 59.742863178253174
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 61.33649778366089
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 15 : 61.349382162094116
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 63.896798849105835
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 15 : 64.62551546096802
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 71.90990018844604
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 15 : 67.64700102806091
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 70.78605484962463
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 15 : 73.54351091384888
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 15--gpu : 69.26962876319885
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 15 : 69.6842188835144
OMP_NUM_THREADS=1 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 27.125267267227173
OMP_NUM_THREADS=1./producer_consumer.py ../jumanji_short.mp4 -n 16 : 27.74042248725891
OMP_NUM_THREADS=2 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 29.469701290130615
OMP_NUM_THREADS=2./producer_consumer.py ../jumanji_short.mp4 -n 16 : 29.09783387184143
OMP_NUM_THREADS=3 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 35.7564640045166
OMP_NUM_THREADS=3./producer_consumer.py ../jumanji_short.mp4 -n 16 : 34.80212116241455
OMP_NUM_THREADS=4 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 39.12517976760864
OMP_NUM_THREADS=4./producer_consumer.py ../jumanji_short.mp4 -n 16 : 38.60938763618469
OMP_NUM_THREADS=5 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 43.24621629714966
OMP_NUM_THREADS=5./producer_consumer.py ../jumanji_short.mp4 -n 16 : 43.54579997062683
OMP_NUM_THREADS=6 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 47.410847187042236
OMP_NUM_THREADS=6./producer_consumer.py ../jumanji_short.mp4 -n 16 : 47.54748177528381
OMP_NUM_THREADS=7 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 49.59942173957825
OMP_NUM_THREADS=7./producer_consumer.py ../jumanji_short.mp4 -n 16 : 48.50709557533264
OMP_NUM_THREADS=8 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 49.58041477203369
OMP_NUM_THREADS=8./producer_consumer.py ../jumanji_short.mp4 -n 16 : 49.66727018356323
OMP_NUM_THREADS=9 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 52.9198055267334
OMP_NUM_THREADS=9./producer_consumer.py ../jumanji_short.mp4 -n 16 : 54.203973054885864
OMP_NUM_THREADS=10 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 54.68943119049072
OMP_NUM_THREADS=10./producer_consumer.py ../jumanji_short.mp4 -n 16 : 54.436747550964355
OMP_NUM_THREADS=11 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 57.35176968574524
OMP_NUM_THREADS=11./producer_consumer.py ../jumanji_short.mp4 -n 16 : 59.34473705291748
OMP_NUM_THREADS=12 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 62.85104727745056
OMP_NUM_THREADS=12./producer_consumer.py ../jumanji_short.mp4 -n 16 : 59.78714036941528
OMP_NUM_THREADS=13 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 67.87423157691956
OMP_NUM_THREADS=13./producer_consumer.py ../jumanji_short.mp4 -n 16 : 61.694342851638794
OMP_NUM_THREADS=14 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 65.04021835327148
OMP_NUM_THREADS=14./producer_consumer.py ../jumanji_short.mp4 -n 16 : 67.56355309486389
OMP_NUM_THREADS=15 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 69.18665146827698
OMP_NUM_THREADS=15./producer_consumer.py ../jumanji_short.mp4 -n 16 : 68.39567422866821
OMP_NUM_THREADS=16 ./producer_consumer.py ../jumanji_short.mp4 -n 16--gpu : 73.04822206497192
OMP_NUM_THREADS=16./producer_consumer.py ../jumanji_short.mp4 -n 16 : 71.55102372169495


tic; naive('../jumanji_short.mp4'); toc : 29s

# Cool stuff

deeplabcut/utils/auxfun_videos.py
