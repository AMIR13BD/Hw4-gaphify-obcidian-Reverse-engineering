# Graph Story — after

The graph suggests the following reverse-engineering narrative. All statements are graph-derived and **require validation in source**.

- Nodes: 25
- Links: 19
- Communities: 7
- Connected components: 7

## Possible Hubs

- **polygons.py** — possible hub (degree 6); graph suggests reviewing `polygons/polygons.py`.
- **Maths Quiz** — possible hub (degree 4); graph suggests reviewing `mathsquiz/README.md`.
- **mathsquiz-step2.py** — possible hub (degree 3); graph suggests reviewing `mathsquiz/mathsquiz-step2.py`.
- **mathsquiz-step3.py** — possible hub (degree 3); graph suggests reviewing `mathsquiz/mathsquiz-step3.py`.
- **Polygon** — possible hub (degree 3); graph suggests reviewing `polygons/polygons.py`.
- **calc_polygon_details()** — possible hub (degree 2); graph suggests reviewing `polygons/polygons.py`.

## Community Overview

- Community 0: 5 nodes
- Community 1: 8 nodes
- Community 2: 4 nodes
- Community 3: 4 nodes
- Community 5: 2 nodes
- Community 6: 1 nodes
- Community 7: 1 nodes

## Investigation Notes

- Use OBS → REL → CONF → CTX → SRC before drawing architecture conclusions.
- God-node candidates are connectivity signals, not confirmed design flaws.
- Compare with `obsidian/hot.md` and node pages for deeper context.
