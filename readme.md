# ShopStat Project

Aim of the project is to gather important statistics for small businesesses, which can include shops, show rooms, gyms barbershops, etc.
For the better conversion, it is important to understand where customers and staff spend the most time. This information helps
to adapt for higher demand on some hours and set up working process.

## Features

Object detection is a technique which allows to localize objects of interest on image. In this case we used YoloV7 object detector to detect persons on the surveillance camera.
That can help us to collect following information:

- Presence Heatmap: allows to understand in which part your customers spend the most time, waiting zone, serving zone or etc.
- Number of customers at a given Time: allows to understand load on your point at specific hours or dates

## Inference speed test

Tested YoloV7-Tiny, YoloV7X Darknet, YoloV7X onnx.
YoloV7x Darknet on CPU shows ambigous long times.
YoloV7-tiny 9ms
Onnx 2ms - the fastest approach
