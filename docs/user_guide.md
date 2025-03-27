This page covers how to configure your tiles once you have the application up and running.

## Connecting to linkding

linktiles can connect to a linkding instance anywhere, they don't need to be hosted on the same machine thanks to the linkding API. Check the [linkding docs](https://linkding.link/api/) to find out how to retrieve your API key. Then navigate to _Settings_ > _Integrations_, and add your API key along with the linkding base url.

Hit _Test & Save_, and if all goes well you should see a successful connection message. The next time you load this page, the API key field will appear empty. Your key is still saved in the database, its just not provided back to you. If you need to retrieve it again, head back to linkding. 

## Creating tiles

In the _Settings_ page, open up the _Tiles_ tab. This is where you can modify your tile layout. If you click the _Help_ button, it will show you an overview of how to configure a tile, those instructions are repeated here.

Click _Add tile_ to create a new tile. This adds a new "protoype tile", which provides the configuration for a single tile in the main view. 

### Fields

The fields on the prototype are as follows:

#### Title

A title to display above the tile. This is optional.

#### Tags

A space-delimited list of tags to use to search for bookmarks to display on the tile. Do not include the hash (`#`). For a bookmark to show up on this tile, it must contain **all** of the listed tags.

#### Limit

The maximum number of bookmarks to display on this tile. Defaults to 100.

#### Groups

A space-delimited list of tags to group the bookmarks on the tile by. An example:

Let's say you have a bunch of recipe bookmarks. They are all marked \#recipes, and some of them are marked \#desserts, and others marked \#vegetarian. You could use "recipes" for the tile tag, and put "desserts vegetarian" in the groups. This would create 3 groups on the tile, one for desserts, one for vegetarian and one for recipes that have neither desserts or vegetarian tags. 

If a bookmark matches more than one group (e.g. a vegetarian dessert), it will be placed in the first matching group.

##### Grouping operators

The groups field also supports a set of grouping operators accessed with the `$` symbol. Consequently, if you need to write a tag that has a dollar sign in it, you must escape it with a backslash (`\$`). The backslash itself must also be escaped (`\\`), as well as the opening and closing brackets. (`\)`, `\(`).

The available grouping operators are as follows:

- `$all(tag1 tag2 tag3)` - Form a group with multiple space-delimited tags. The captured links must belong to all tags in the list.
- `$any(tag1 tag2 tag3)` - Form a group with multiple space-delimited tags where the captured links must belong to at least one of the tags in the list.
- `$named(title tag)` - Create a group with a title. Accepts a title and a tag separated by a space. If you want to include a space in the title, you can escape the space with a backslash.
- `$ungrouped` - A reference to the ungrouped links, you can use this to create a named grouped with them or choose what order they appear in.

Grouping operators can also be freely nested within each other, for example: `$named(1\ to\ 3 $any(tag1 tag2 tag3))` would produce a named group "1 to 3", that contains all bookmarks with any of the tags `tag1`, `tag2`, `tag3`. The only limitation is you can't nest a `$named` group inside another `$named` group.

### Reordering tiles

Drag the handle on the left of the prototype to reorder the tiles. You can click the remove button in the bottom right to delete the prototype.

Once you're all done, be sure to hit the _Save_ button!

## General settings

Switching over to the `General` tab will give you options on how to render the tile mosaic. This is where you will also find the option to change your password.

### Tile look and feel

#### Tile colors

This sets the colors of the tiles.

- Random: randomly pick a color (roughly 50/50 chance of getting a dark or bright color) and assign it to the tile, keeping the same color for the lifetime of the tile.
- Really Random: re-pick the color every time the page loads
- Dark: only use dark colors
- Bright: only use bright colors
- Darker: increase the bias towards dark colors
- Brighter: increase the bias towards light colors

#### Tile fill

How to fill in the tile color.

- Fill: solid color
- Outline: border only
- Ghost: no fill

#### Title location

Where to display the tile title.

- Inside: inside the tile
- Outside: above the tile

#### Tile layout

How to arrange the tiles in the mosaic.

- Masonry: maintain regular columns while squeezing the tiles as close together as possible vertically, giving a staggered layout
- Grid: a tabular grid of regular rows and columns
- List: a single vertical list

#### Tile width

The target width, in pixels, for each tile.

#### Tile group layout

How to arrange the bookmarks within a group.

- Default: list out the bookmarks one after another, like text in a paragraph
- Loose: add extra space in between the bookmarks
- List: a single vertical list
- Columns: arrange the bookmarks in regular columns within the tile

#### Bookmark sort

How to order the bookmarks within a group.

- Default: leave them ordered as they come from linkding
- Alphabetical: alphabetical order
- Last Modified: start with the most recently modified bookmark
- Last Added: start with the most recently added bookmark
- First Added: start with the least recently added bookmark

### linkding options

#### Cache responses

Cache responses from linkding, to increase responsiveness and reduce the number of API calls. You can configure how long you want the cache to last.

### Data management

#### Data export

You can export your tile configuration for safe keeping.

## Integrations

On the _Integrations_ tab, aside from the linkding integration, linktiles can integrate with some other services.

### Glance

This token can be used to connect to display your tiles in Glance. The tiles will be rendered using Glances style classes.

In order to connect, Glance needs to make requests to linktiles using the provided token in the authorization header. Glance added support for this in version **v0.7.8**, so you must use at least that version.
Below is an example Glance configuration. This requires the `allow-potentially-dangerous-html` flag to render everything correctly. 

```yaml title='glance.yml'
pages:
  - name: Home
    columns:
      - size: full
        widgets:
          - type: extension
            url: http://glance-linktiles-proxy/integrations/glance
            allow-potentially-dangerous-html: true
```

!!! note

    If you are using `LT_ENABLE_AUTH_PROXY` and protecting your entire linktiles path, you will run into issues
    if Glance is not able to get through your auth proxy. In this case you may want to modify your proxy such that the 
    `/integrations/glance` route can skip authentication. linktiles recognizes this route and will explicitly require a valid
    authorization token.

