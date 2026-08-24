# GEMA Design System - Reference for Claude

## Overview
This document is specifically crafted as a reference guide for AI assistants (like Claude) when building or modifying React components in this workspace. It explicitly lists the GEMA design tokens, colors, hex codes, and typography classes that must be mapped to all UI elements instead of hardcoded values.

## Colors & Hex Values (Tokens)
Components must rely exclusively on these CSS variables defined in `:root` (from `FoundationsGema/styles.css`). Never use hardcoded hex values in component files; use `var(--token-name)` or a corresponding Tailwind utility if mapped in `tailwind.config.js`.

### Neutral
*   `--neutral/100`: `#28363E` (High-contrast text)
*   `--neutral/90`: `#536E79` (Mid-contrast text and icons without labels)
*   `--neutral/80`: `#698996`
*   `--neutral/70`: `#879DAB` (Low-contrast text and icons with labels)
*   `--neutral/60`: `#A6B6BF`
*   `--neutral/50`: `#C4CED4`
*   `--neutral/40`: `#DCE1E5`
*   `--neutral/30`: `#F0F2F4` (Tertiary background)
*   `--neutral/20`: `#F8FAFB` (Secondary background)
*   `--neutral/10`: `#FFF` (App background, on solid background)

### Primary (Blue)
*   `--primary/100`: `#16316B`
*   `--primary/90`: `#1E52C6` (Strong solid background, High-contrast text and icons)
*   `--primary/80`: `#2F71E5` (Solid background, Mid-contrast text and icons)
*   `--primary/70`: `#6090F1` (Soft solid background, Low-contrast text and icons)
*   `--primary/60`: `#83ADFF`
*   `--primary/50`: `#AAC8FF`
*   `--primary/40`: `#C8DBFF`
*   `--primary/30`: `#E4EDFF` (Secondary background and stroke)
*   `--primary/20`: `#F3F7FF` (Primary background)
*   `--primary/10`: `#F8FAFB`

### Green (Success)
*   `--green/100`: `#003B0A`
*   `--green/90`: `#006A1A` (Strong solid background, High-contrast text and icons)
*   `--green/80`: `#008523` (Solid background, Mid-contrast text and icons)
*   `--green/70`: `#2BA53D` (Soft solid background, Low-contrast text and icons)
*   `--green/60`: `#50C45B`
*   `--green/50`: `#6CDE74`
*   `--green/40`: `#7FF186`
*   `--green/30`: `#B7FFB9` (Secondary background and stroke)
*   `--green/20`: `#E7FFE8` (Primary background)
*   `--green/10`: `#FAFFFA`

### Yellow (Warning)
*   `--yellow/100`: `#463200`
*   `--yellow/90`: `#765600` (Strong solid background, High-contrast text and icons)
*   `--yellow/80`: `#966F00` (Solid background, Mid-contrast text and icons)
*   `--yellow/70`: `#BB8B00` (Soft solid background, Low-contrast text and icons)
*   `--yellow/60`: `#DAA205`
*   `--yellow/50`: `#FBC141`
*   `--yellow/40`: `#FCD579`
*   `--yellow/30`: `#FCEDB9` (Secondary background and stroke)
*   `--yellow/20`: `#FDF8D9` (Primary background)
*   `--yellow/10`: `#FEFCF0`

### Orange
*   `--orange/100`: `#5F1A05`
*   `--orange/90`: `#A82C00` (Strong solid background, High-contrast text and icons)
*   `--orange/80`: `#C84801` (Solid background, Mid-contrast text and icons)
*   `--orange/70`: `#ED6704` (Soft solid background, Low-contrast text and icons)
*   `--orange/60`: `#FF8C51`
*   `--orange/50`: `#FBB99A`
*   `--orange/40`: `#FFCFB9`
*   `--orange/30`: `#FFE9E0` (Secondary background and stroke)
*   `--orange/20`: `#FFF5F1` (Primary background)
*   `--orange/10`: `#FFFBFA`

### Red (Error/Destructive)
*   `--red/100`: `#600A00`
*   `--red/90`: `#AF1B00` (Strong solid background, High-contrast text and icons)
*   `--red/80`: `#D74028` (Solid background, Mid-contrast text and icons)
*   `--red/70`: `#F65D44` (Soft solid background, Low-contrast text and icons)
*   `--red/60`: `#FF8973`
*   `--red/50`: `#FFB6A7`
*   `--red/40`: `#FFCDC3`
*   `--red/30`: `#FFE9E4` (Secondary background and stroke)
*   `--red/20`: `#FEF5F3` (Primary background)
*   `--red/10`: `#FFFBFA`

### Charts
*   `--chart/1`: `#0050AE`
*   `--chart/2`: `#002F64`
*   `--chart/3`: `#33B983`
*   `--chart/4`: `#008C5C`
*   `--chart/5`: `#F98517`
*   `--chart/6`: `#C85B00`
*   `--chart/7`: `#AC0000`
*   `--chart/8`: `#561E01`

## Typography Classes
When applying text styling in React components, do **not** construct font size and line-heights manually via Tailwind (like `text-[18px] leading-[24px]`). Instead, use the pre-defined GEMA CSS classes from `FoundationsGema/styles.css`:

### Mobile Headings
*   `.headings-mobile-mh1`: Semi Bold, 28px, LH 32px
*   `.headings-mobile-mh2`: Semi Bold, 24px, LH 32px
*   `.headings-mobile-mh3`: Semi Bold, 18px, LH 24px

### Web Headings
*   `.headings-web-h1`: Semi Bold, 60px, LH 64px
*   `.headings-web-h2`: Semi Bold, 48px, LH 56px
*   `.headings-web-h3`: Semi Bold, 36px, LH 40px
*   `.headings-web-h4`: Semi Bold, 28px, LH 32px
*   `.headings-web-h5`: Semi Bold, 24px, LH 32px
*   `.headings-web-h6`: Semi Bold, 18px, LH 24px

### Paragraphs & Body
*   `.paragraphs-large`: Regular, 20px, LH 32px
*   `.paragraphs-largesemibold`: Semi Bold, 20px, LH 32px
*   `.paragraphs-medium`: Regular, 16px, LH 24px
*   `.paragraphs-mediumsemibold`: Semi Bold, 16px, LH 24px
*   `.paragraphs-small`: Regular, 14px, LH 20px
*   `.paragraphs-smallsemibold`: Semi Bold, 14px, LH 20px
*   `.paragraphs-disclaimer`: Regular, 12px, LH 18px
*   `.paragraphs-disclaimersemibold`: Semi Bold, 12px, LH 18px
*   `.paragraphs-navigation`: Regular, 10px, LH 16px

## Spacing & Radius Tokens
Map spacing (padding/margin/gap) and border-radius using the provided CSS variables:
*   **Radius:** `--radius_0`, `--radius_2`, `--radius_4`, `--radius_6`, `--radius_8`, `--radius_12`, `--radius_16`, `--radius_24`, `--radius_32`, `--radius_full` (999px)
*   **Padding/Spacing:** Increments of 0, 2, 4, 6, 8, 10, 12, 16, 20, 24, 28, 32, 36, 40, 48, 64, 96 (e.g., `--spacing/spacing_16` for 16px, `--padding/padding_24` for 24px)
