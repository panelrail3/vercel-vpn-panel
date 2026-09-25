# Vercel VPN Config Panel

Vercel can host the web panel, but it is not a replacement for a persistent Xray/VPN server. Put Xray on Railway/VPS and set:

XRAY_PUBLIC_HOST=your-xray-domain
XRAY_PUBLIC_PORT=443

The Vercel URL is the panel URL. Generated VPN links point to XRAY_PUBLIC_HOST/XRAY_PUBLIC_PORT.
