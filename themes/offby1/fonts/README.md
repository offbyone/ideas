# Custom Fonts

This directory contains custom web fonts that are used by the theme.

## MonoLisa

MonoLisa is a commercial font used for code blocks. The font files are:

- MonoLisa-Regular.woff2 / MonoLisa-RegularItalic.woff2 (weight 400)
- MonoLisa-Light.woff2 / MonoLisa-LightItalic.woff2 (weight 300)
- MonoLisa-Medium.woff2 / MonoLisa-MediumItalic.woff2 (weight 500)
- MonoLisa-SemiBold.woff2 / MonoLisa-SemiBoldItalic.woff2 (weight 600)
- MonoLisa-Bold.woff2 / MonoLisa-BoldItalic.woff2 (weight 700)

These fonts are copied to `themes/offby1/static/webfonts/` during the build process via the `prepare_fonts` task in the justfile.

## Build Process

The fonts are automatically copied during builds via:

```bash
just prepare_fonts
```

This is called automatically as part of `just build`.
