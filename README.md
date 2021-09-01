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

**BitAnime** is a python script that allows you to download anime in large batches. It can also be used to download anime films. **BitAnime** gets its content from [gogoanime](https://gogoanime.pe/). If you get a **404** error, please look up the correct anime name on [gogoanime](https://gogoanime.pe/). This application can only download **1**-**99** episodes at the time. At the moment, the quality of the episodes that will be downloaded is different for every anime. For **older anime**, the quality will be **360p** to **480p**, for **newer anime** the quality will be **720p** to **1080p**.

## Installation

```console
git clone https://github.com/sh1nobuu/BitAnime.git
```

## Screenshot

<div align="center">
  <img src="https://i.postimg.cc/q76DzZ5y/ba-screenshot.png"
  title="BitAnime in action" alt="BitAnime Screenshot">
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
