# Third-party data and licensing

## World map / coastline geometry

The original prototype generated coastlines and country outlines from Basemap's
bundled GSHHS/GSHHG low-resolution geographic data, later serialized as SVG
paths in `assets/world-startup.html` and the prebuilt `lib/client.js`.

Source: Global Self-consistent, Hierarchical, High-resolution Geography (GSHHG)
Authors: Paul Wessel (University of Hawai'i) and Walter H. F. Smith (NOAA)
Project: https://www.soest.hawaii.edu/wessel/gshhg/
Data notice: https://www.ngdc.noaa.gov/mgg/shorelines/shorelines.html
Publication: Wessel, P. and W. H. F. Smith (1996), J. Geophys. Res. 101(B4),
8741–8743, doi:10.1029/96JB00104.

GSHHG is distributed under the GNU Lesser General Public License (LGPL);
the official notice and full LGPL v3 text are included separately in
`licenses/GSHHG-LGPL-3.txt`. Derived SVG outline data remains subject to those
terms. Do not misinterpret the project's MIT code license as relicensing map data.

## TNO/LAR visual inspiration

This is an independently implemented interface inspired by the aesthetic of
The New Order / Long and Arduous Road. It is not the original game code,
not endorsed by the game/mod authors, and embeds no original game UI textures.
All system metrics and links are fictional visual demonstrations.