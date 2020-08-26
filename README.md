ShenZhen OPL for Eagle Library Generator
----------------------------------------

while designing a pcb board for manufacturing at seedstudio Fusion PCBA, I had a lot of issues finding the right parts I needed. 
I had to spend a lot of time doing manual adding of components to libraries, and editing the BOM with correct data.
so I decided to build a tool that would auto generate eagle library with information downloaded directly from the website.

#current status
the software is currently in Proof Of Concept. as a first stage I focus on the Resistors-Capacitors-Inductors category as they are relatively easy to parse.
component are sorted and grouped by value, so for example "1R-5%-1/8W" will contain all footprints and manufacturers as variant.
footprint samples are grabbed from the built-in eagle libraries. 

#contributing
help is welcome. it started as a weekend project, but as I wrote more and more it came clear to me it is a long project. you're welcome to contact me for more information
