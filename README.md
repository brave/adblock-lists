# Lists

Brave heavily uses the community-maintained [EasyList](https://easylist.to/), [EasyPrivacy](https://github.com/easylist/easylist/tree/master/easyprivacy) and [uBlock Origin](https://github.com/uBlockOrigin/uAssets) filter lists by default to block ads and trackers. This repo collects additional filter lists beyond those upstream lists. You can see which filter lists are used and enabled by default in the [list catalog](https://github.com/brave/adblock-resources/blob/master/filter_lists/list_catalog.json). 

Over time, this repo has started collecting all privacy-related lists, not just adblock filter lists. 

Backend logic for downloading and shipping these lists out to clients is in https://github.com/brave/brave-core-crx-packager. If you add a new list here, you will need changes there too. See section below on adding a new list.
Also see https://github.com/brave/adblock-resources for accompanying resources needed by filter lists.


## Testing

If modifying the `debounce.json` or `clean-urls.json` lists, follow [these instructions](https://github.com/brave/brave-browser/wiki/Debouncing#testing-new-rules) to test your changes locally.

## Adding a new non-adblock list


If you're adding an adblock filter list (i.e. meant for consumption by adblock-rust in brave-core), skip this section and see below. 

In most cases, a new list belongs in a new CRX component. Lists added in this repo need to be fetched and packaged by https://github.com/brave/brave-core-crx-packager to actually be shipped out to Brave browser clients in a CRX component. Also, Brave browser clients need to know to download and register the new component. Please see https://github.com/brave/brave-core/edit/master/docs/ship_a_file_to_all_clients.md for a comprehensive guide on how to do this.

If the new list is to be added to an _existing_ component (with existing brave-core support), you can skip the component generation and brave-core steps, and instead just add support for downloading your new list in crx-packager. This is NOT usually recommended; most new lists need their own dedicated component. Search for where existing files are being downloaded for the component you're adding to.

## Adding a new adblock filter list

The CRX packager loads adblock filter lists from the [adblock-resources list catalog](https://github.com/brave/adblock-resources/blob/master/filter_lists/list_catalog.json). This list catalog contains a list of all of the filter lists that are active on Brave. To add a filter list from this repo to the list catalog, you first need to get a link to the raw file. This link should look like `https://raw.githubusercontent.com/brave/adblock-lists/master/brave-lists/brave-social.txt`.

When adding a new filter list to an existing component (adding another list to Brave Default Adblock Filters component, for example), just add another source to that component in the adblock-resouces list catalog, making sure to use the link to the raw file as the `url`.

When adding a new component to the adblock-resources list catalog, see https://github.com/brave/adblock-resources#adding-a-new-list for a guide on how to create the component and register the component on Brave browser clients.
