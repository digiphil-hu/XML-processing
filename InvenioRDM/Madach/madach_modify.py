from xml_methods import get_filenames, normalize, prettify_soup

path_list = ["/home/pg/Documents/GitHub/Madach_Az_ember_tragediaja/Megállapított-szöveg"]

for parsed, path in get_filenames(path_list):
    main_title = normalize(parsed.find("title", {"type": "main"}).text.replace("-", " - ").replace("ember", "ember "))
    new_title = (main_title.replace(", szinoptikus digitális kritikai kiadás", "").rstrip(".").replace("-", "–")
                 + " (megállapított szöveg).")
    parsed.find("title", {"type": "main"}).string = new_title
    print(parsed.find("title", {"type": "main"}))
    with open(path, "w", encoding="utf8") as f:
        f.write(prettify_soup(parsed))