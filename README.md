<div align="center">
  <img
    style="width: 165px; height: 165px"
    src="https://i.postimg.cc/VkSMVQrg/ba-logo.png"
    title="BitAnime"
    alt="BitAnime"
  />
  <h3>BitAnime</h3>
  <p>
    A Python script that allows you to download all of an anime's episodes at once.
  </p>
  <a href="https://github.com/sh1nobuu/BitAnime/releases"> <strong>· Download executable version ·</strong></a>
</div>

## About BitAnime

**BitAnime** is a python script that allows you to download anime in large batches. It can also be used to download anime films. **BitAnime** gets its content from [gogoanime](https://gogoanime.pe/). If you get a **404** error, please look up the correct anime name on [gogoanime](https://gogoanime.pe/). The application will let you download all the episodes, or you can choose how many episodes you want to download.

## Installation

```console
git clone https://github.com/sh1nobuu/BitAnime.git
```

## Screenshot

<div align="center">
  <img style="height:386px; width:688px;" src="https://i.postimg.cc/cLgf8994/ba-screenshot.png"
  title="BitAnime in action" alt="BitAnime Screenshot">
  <img style="height:386px; width:688px;" src="https://i.postimg.cc/G2qGDpfV/downloade.png" title="Katekyo Hitman Reborn" alt="Downloaded anime with BitAnime">
</div>

## Dependencies

**BitAnime** is highly reliant on the python modules `requests`, `colorama`, `tqdm`, and `BeautifulSoup`.

```console
pip install -r requirements.txt
```

## Usage

The anime name is separated by "-". You can either type it manually, or go to [gogoanime.pe](https://gogoanime.pe/) and search for the anime you want to download and copy the name from the URL.

### Examples

##### One word title

- https://gogoanime.pe/category/bakemonogatari >> bakemonogatari
- https://gogoanime.pe/category/steinsgate >> steinsgate

##### Multiple word title

- https://gogoanime.pe/category/shadows-house >> shadows-house
- https://gogoanime.pe/category/kono-subarashii-sekai-ni-shukufuku-wo- >> kono-subarashii-sekai-ni-shukufuku-wo-
