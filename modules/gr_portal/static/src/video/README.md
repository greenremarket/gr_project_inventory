# gr_portal — video assets

`greenremarket2.mp4` must be present in this directory but is **not tracked in git** (too large for a repo asset).

## How to obtain it

Copy from the design prototype repo:

```
git clone https://github.com/moradigmir/remix-of-green-remarket-portal-refresh
cp remix-of-green-remarket-portal-refresh/public/videos/greenremarket2.mp4 \
   modules/gr_portal/static/src/video/greenremarket2.mp4
```

Or copy from a production server that already has the file deployed at
`<odoo_data_dir>/addons/gr_portal/static/src/video/greenremarket2.mp4`.

## Deployment

When deploying to a new server, copy the video to the module's static path
**before** installing the module.  The Odoo asset bundler does not move
static files — they are served directly at `/gr_portal/static/src/video/…`.
