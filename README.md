# Custom Mouse Cursor

## Posy Black
This is a slightly altered version of [Posy's Cursor Black](http://www.michieldb.nl/other/cursors)

<img src="./Posy_Black/Arrow.svg" alt="Arrow" width="32"/><img src="./Posy_Black/AppStarting.svg" alt="AppStarting" width="32"/><img src="./Posy_Black/Wait.svg" alt="Wait" width="32"/><img src="./Posy_Black/Hand.svg" alt="Hand" width="32"/><img src="./Posy_Black/IBeam.svg" alt="IBeam" width="32"/><img src="./Posy_Black/No.svg" alt="No" width="32"/><img src="./Posy_Black/SizeAll.svg" alt="SizeAll" width="32"/><img src="./Posy_Black/SizeNESW.svg" alt="SizeNESW" width="32"/><img src="./Posy_Black/SizeNS.svg" alt="SizeNS" width="32"/><img src="./Posy_Black/SizeNWSE.svg" alt="SizeNWSE" width="32"/><img src="./Posy_Black/SizeWE.svg" alt="SizeWE" width="32"/><img src="./Posy_Black/Person.svg" alt="Person" width="32"/><img src="./Posy_Black/Pin.svg" alt="Pin" width="32"/><img src="./Posy_Black/Help.svg" alt="Help" width="32"/><img src="./Posy_Black/Crosshair.svg" alt="Crosshair" width="32"/><img src="./Posy_Black/NWPen.svg" alt="NWPen" width="32"/><img src="./Posy_Black/UpArrow.svg" alt="UpArrow" width="32"/>

# How to install
- Open the folder containing the cursors you want to install
- Right click the `_install .inf` file and click `Install`
- The cursors install automatically (You must agree to the installation) and will open "Mouse Properties" menu. You need to press the "OK" button.

# How to build
All cursors are created with `.svg` files. A python script converts those to their respective `.cur` or `.ani` file.
- Edit an SVG file.
- Run `convert_all.bat` to convert all SVG files.
- Optionally, you can run the script with an extra argument `--output-png` to keep the png files.

### Hotspot
With the custom attribute `hotspot="x y"` you can set the hotspot of the cursor. The XY coordinates are relative to the `viewBox`.

### Animation
Currently only `animateTransform` with a `linear` interpolation of `transform` is supported. With the custom attribute `frameCount` you can change the amount of frames of the animation.