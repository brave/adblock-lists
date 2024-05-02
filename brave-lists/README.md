# Brave Lists

Various lists that are used in the Brave browser, including:

- `clean-urls.json` for [Copy clean link](https://github.com/brave/brave-browser/wiki/Copy-clean-link)
- `debounce.json` for the [debouncer](https://github.com/brave/brave-browser/wiki/Debouncing)

### Adding a new list to a browser component

After adding the list here, you will have to also add it to the crx-packager: https://github.com/brave/brave-core-crx-packager/. Here's an example PR that adds a new list (that lives here) to the `Brave Local Data Updater` component: https://github.com/brave/brave-core-crx-packager/pull/562
