#!/bin/sh

httrack http://spdx.org/licenses/ \
  -O SPDX_Licenses.docset/Contents/Resources/Documents,cache -I0 \
  --display=2 --timeout=60 --retries=99 --sockets=7 \
  --connection-per-second=5 --max-rate=250000 \
  --keep-alive --depth=4 --mirror --robots=0 \
  --user-agent '$(httrack --version); dash-spdx-licenses ()' \
  "-*" "+http://spdx.org/licenses/*" "-http://spdx.org/licenses/[*"
