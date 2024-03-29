# Log for updates
All logs of new updates and releases will be written here

<b>Release 1.0.1</b><i> from 08.06.2023</i>
<br>
Working only with Audio and Video (not longer than 3-4min)
<br>
<b>P.S.</b>Video can be unstable and not working properly on iOS and MacOS

<b>Release 1.0.2</b><i> from 10.06.2023</i>
<br>
1) Fixed a bug with sending videos with an aspect ratio of 1:1. Now all videos are sent in the original aspect ratio.
2) Fixed a bug related to recursion in the menu after sending media content
3) Playback on iOS and macOS is now convenient and comfortable
4) Added the output of the video title in the description to the media content
5) Added notification of 50 MB limit

<b>Release 1.0.3</b><i> from 11.06.2023</i>
<br>
1) The bot works even faster
2) Added the output of the rating, the author of the channel and the number of views

<b>Release 1.1.0</b><i> from 13.06.23</i>
<br>
1) Bot now works on <code>asyncio</code> and <code>aiohttp</code>
2) Script structure has been completely redesigned
3) Redesigned interaction with the bot and commands
4) Full stability of operation is provided
5) Code has been optimized and simplified for the convenience of working with it
6) The so-called "fool test" has been added. When requesting a media link, <br>if the incoming message is not a link, the bot will give an error

<b>Release 1.1.1</b><i> from 22.06.23</i>
<br>
1) Removed unused functions, imports etc. <br>
2) Code has been optimized and working faster<br>
3) Added error handler (e.g. age restricted videos, which can only be viewed by logging in)<br>
4) Some text corrections<br>
5) Fixed <code>pytube</code> error: <code>get_throttling_function_name: could not find match for multiple</code><br>
6) Fixed bug with recursion after pressing "Главное меню" button

<b>Release 1.1.2</b><i> from 12.07.23</i>
<br>
1) Fixed error with default_filename <br>
2) Added downloading from VK Videos and VK Clips<br>
3) Quality choosing step for VK<br>

<b>Release 1.1.3</b><i> from 22.07.23</i>
<br>
1) Added functionality to search YouTube videos in Telegram
2) Text corrections
3) Fixed <code>get_transform_object: could not find match for var for={(.*?)};</code> error
   
