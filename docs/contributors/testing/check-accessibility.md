(check-accessibility)=
# Check your interface for accessibility

This guide will help you address common accessibility pitfalls in apps and interfaces on Ubuntu Desktop. This aligns with the [Ubuntu mission](https://ubuntu.com/community/ethos/mission): we believe that every computer user should be able to use all software regardless of disability.

## Why accessibility is important

Designing and coding for accessibility helps everyone, not just a specific group. People with disabilities or age-related challenges that affect seeing, hearing, moving, speaking, or understanding information need accessible design. But disabilities can also be temporary or situational, like having an injury, being in a noisy place, or dealing with glare.

We aim to comply with the [Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/), level AA. WCAG has been adopted as the standard for accessibility legislation around the world. The guidelines ensure that the interface is:

Perceivable
: All users can perceive it

Operable
: All users can interact with it

Understandable
: All users can comprehend it

Robust
: The interface is compatible with accessibility features (also called assistive technologies)

## Enable accessibility features

You can access all accessibility features in Ubuntu Desktop in the Settings app, under {guilabel}`Accessibility`. There, you can also enable the accessibility menu for quick access from the top bar.

You can read more about accessibility features in Ubuntu in the [Ubuntu Desktop documentation](https://canonical-ubuntu-desktop-documentation.readthedocs-hosted.com/en/latest/how-to/accessibility/).

## Check visual accessibility

These checks support people with low vision (cataracts), color vision deficiencies (color blindness), photosensitivity, or reading difficulties by ensuring clear contrast, readable text at any size, no reliance on color alone, and safe, non-distracting visuals.

### Enable the visual features

High contrast mode
: Go to {menuselection}`Settings --> Accessibility --> Seeing`, enable {guilabel}`High Contrast`. You can also enable {guilabel}`High Contrast` in the Accessibility menu.

Dark theme
: Go to {menuselection}`Settings --> Appearance --> Style`, select {guilabel}`Dark`.

Large text
: Go to {menuselection}`Settings --> Accessibility --> Seeing`, enable {guilabel}`Large Text`. You can also enable {guilabel}`Large Text` in the Accessibility menu.

### Visual accessibility checklist

- All elements are visible and all text is legible in light theme
- All elements are visible and all text is legible in light theme with high contrast mode enabled
- All elements are visible and all text is legible in dark theme with high contrast mode enabled
- All text wraps instead of overflowing/cropping when enabling large text mode
- All text wraps instead of overflowing/cropping when the window is resized
- Meaning is conveyed through text or icons, not by color alone.
    * For example: for errors, an error message is shown in addition to a red border.
- Animations are disabled for users that have {guilabel}`Animation Effects` disabled in the Settings app ({menuselection}`Settings --> Accessibility --> Seeing`).
- No flashing (there should be less than 3 flashes per second)
- All elements have enough contrast with their background
    * Read [Contrast checks](#contrast-checks) for further guidance.

### Contrast checks

Although contrast is usually handled at the theme level, you should ensure all elements have enough color contrast so all text and controls are perceivable:

- For text: 4.5:1 or higher contrast with background
- For everything else (for instance, icons on background): 3:1 or higher contrast with background

For checking **color contrast**, install a checker such as [Kontrast](https://snapcraft.io/kontrast) or [Contrast](https://flathub.org/apps/org.gnome.design.Contrast), and pick the foreground and background colors.

You should be particularly cautious in the following cases:

- Check how your local style overrides affect states like hover or focus
- Check light colors, such as light gray for secondary text or yellow
- Check semantic colors for text, such as red for errors or yellow for warnings. Compare light and dark theme

No minimum contrast is required for inactive components, decorative images or graphics, or logos.

## Check keyboard navigation

These checks ensure a good experience for keyboard-only users, including people with motor disabilities that cannot use a mouse or trackpad, blind users who rely on screen readers, and power users who just prefer to use their keyboard.

### Try keyboard shortcuts

For a simple test, select the window you want to test. Then hit the {kbd}`Tab` key repeatedly and check how focus moves through all interactive elements.

For a more thorough test, you need these shortcuts:

| Action | Shortcut |
|--------|----------|
| Move to next interactive item | {kbd}`Tab` |
| Move to previous interactive item | {kbd}`Shift+Tab` |
| Interact with an item or group | {kbd}`Enter` |
| Exit a group | {kbd}`Esc` |
| Move between windows/main area, top bar and dashboard | {kbd}`Ctrl+Tab` |

### Keyboard navigation checklist

- All interactive elements (buttons, fields, links…) are focusable by using the {kbd}`Tab` key
- All interactive elements have a visible focus state (ideally a focus ring)
- There are no focus traps: it is possible to escape all loops, for instance by hitting the {kbd}`Esc` key
- Focus moves from one element to the next in a logical order
    * In most of our apps, that usually means sidebar (if open), then body; and top to bottom, left to right (or right to left for RTL languages such as Arabic or Hebrew).
- Focus moves to modals/dialogs when opened, and returns to the trigger when closed
- Modals close by hitting the {kbd}`Escape` key
- If an element doesn’t have a visible label but does have a tooltip on hover, the tooltip should also be visible on focus

## Check screen reading

All graphical interfaces in Ubuntu Desktop should be readable with the built-in [Orca screen reader](https://canonical-ubuntu-desktop-documentation.readthedocs-hosted.com/en/latest/how-to/accessibility/read-screen-aloud/). Screen readers benefit blind and visually impaired users who rely on audio feedback to navigate interfaces. To work properly, screen readers require good markup, labelling, and logical content structure.

### Use the screen reader

The Orca screen reader can be enabled in {menuselection}`Settings --> Accessibility --> Seeing`. You can also enable {guilabel}`Screen Reader` in the Accessibility menu.

Note that some Orca features don’t work with certain combinations of Ubuntu releases and application toolkits. Read [Improve screen reader usability](https://canonical-ubuntu-desktop-documentation.readthedocs-hosted.com/en/latest/how-to/accessibility/improve-screen-reader-usability/).

You need to get familiar with keyboard shortcuts to use the screen reader. Modifier keys are used in the shortcuts:

{kbd}`Super`
: Generally mapped to the {kbd}`Windows` key on Windows computers, and the {kbd}`Command` key on Macs.

{kbd}`Orca`
: By default, the Orca key is {kbd}`CapsLock` for the Laptop layout, and the {kbd}`Insert` key for the Desktop layout. You can [set the layout](https://canonical-ubuntu-desktop-documentation.readthedocs-hosted.com/en/latest/tutorial/get-started-with-the-screen-reader/#determine-your-keyboard-layout) in the Orca settings, typing {command}`orca -s` in the terminal.
    
| Action | Laptop layout | Desktop layout |
|--------|-----------------------------------|------------------------------------|
| Enable screen reader | {kbd}`Super+Alt+S` | {kbd}`Super+Alt+S` |
| Quit screen reader | {kbd}`Super+Alt+S` | {kbd}`Super+Alt+S` |
| Learn mode | {kbd}`Orca+H` (exit with {kbd}`Esc`) | {kbd}`Insert+H` (exit with {kbd}`Esc`) |
| Orca preferences | {kbd}`CapsLock+Space` | {kbd}`Insert+Space` |
| Toggle flat review | {kbd}`CapsLock+P` | {kbd}`Insert+-` on the numeric keypad |
| Say all (in flat review) | {kbd}`CapsLock` and double-press {kbd}`;` | Double-press {kbd}`+` on the numeric keypad |
| Read current line | {kbd}`CapsLock+I` | {kbd}`8` on the numeric keypad |
| Read next line | {kbd}`CapsLock+O` | {kbd}`9` on the numeric keypad |
| Read previous line | {kbd}`CapsLock+U` | {kbd}`7` on the numeric keypad |

You can find further guidance in the [screen reader documentation](https://canonical-ubuntu-desktop-documentation.readthedocs-hosted.com/en/latest/how-to/accessibility/read-screen-aloud/).

### Screen reading checklist

- All interactive elements (buttons, fields, links…) have a label and a role that is read out loud by the screen reader
    * Roles explain the function of the component (“button”, “text”, “link”, “combobox”). Check [GTK roles](https://docs.gtk.org/gtk4/enum.AccessibleRole.html).
- There are no two or more elements with the same label in the same page
    * For example, if there’s a single share button, it can be labeled “Share”. But if there’s more than one “Show” button, you should specify what it refers to: “Show description”, “Show gallery”.
- All labels are short, descriptive and meaningful
    * Take context into account: if you are on an app page, the share button should be labeled “Share”, not “Share this app” or “Share [app name]”: it’s generally redundant with the page title/headings.
- All pages have a meaningful title or main heading
- All sections within a page have a meaningful heading
- When changing to a new page, either page title or the main heading is announced (whichever is more meaningful)
- Errors are either announced or readable with the screen reader
- For images that are not strictly decorative, provide alternative text that can be read out loud by the screen reader
    * Get guidance on how to write good alternative text in the [Vanilla content guidelines](https://vanillaframework.io/docs/content-guidelines#alt-text-for-images)
- For audio or video content, provide text alternatives (for instance, transcriptions or captions)

## Check additional accessibility

Besides the more common checks above, you should also keep in mind these:

- All UI text is reasonably short and easy to understand
    * Check the [GNOME Human Interface Guidelines](https://developer.gnome.org/hig/guidelines/writing-style.html) and the [Vanilla content guidelines](https://vanillaframework.io/docs/content-guidelines) for guidance.
- When there’s an error submitting data or in a flow, a meaningful error message is shown
    * Good error messages explain to the user how to avoid them, or at least explain the cause of the error.
- Search functionality is provided whenever possible so users have an alternative way to find the page or section they are looking for
- Leave space between interactive items
    * This [helps users with tremors](https://axesslab.com/hand-tremors/)
- Audio that lasts more than 3 seconds does not play automatically
- Audio that lasts more than 3 seconds can be paused or muted

## Look for user feedback

When auditing an app, check any outstanding accessibility issues in the app repository. Actual users are the best source for accessibility issues.

## Report accessibility issues

If you found an accessibility issue, please open an issue in the relevant repository. Repositories for Ubuntu software are generally hosted on either [Launchpad](https://bugs.launchpad.net/ubuntu) or [GitHub](https://github.com/ubuntu). Describe the issue in as much detail as you can, and provide instructions to test it. Screenshots and screen recordings also help. You can propose a fix for the issue, but it’s not strictly necessary.

## References

* [Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/) 
* [Accessibility - GNOME Human Interface Guidelines](https://developer.gnome.org/hig/guidelines/accessibility.html)
* [Disability Simulator](https://www.disabilitysimulator.com/)