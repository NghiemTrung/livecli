from importlib import import_module
from os import listdir
from os import makedirs
from os import path


def create_dict_from_plugins():
    plugins_path = path.join("..", "src", "livecli", "plugins")
    modules = sorted(listdir(plugins_path))

    exclude = [
        "__init__.py",
        "__pycache__",
        "akamaihd.py",
        "common_jwplayer.py",
        "common_swf.py",
        "hds.py",
        "hls.py",
        "http.py",
        "resolve.py",
        "rtmp.py",
    ]

    docs_dict = {}
    for module in modules:
        if module in exclude or module[-3:] != ".py":
            continue
        name = module[:-3]
        module_name = "livecli.plugins.{0}".format(name)
        try:
            mod = import_module(module_name)
            docs_dict[name] = mod.__livecli_docs__
        except AttributeError:
            docs_dict[name] = {}
            print("Missing __livecli_docs__ in {0}".format(module_name))
    return docs_dict


def setup(app):
    length_plugin_name = 15
    length_domains = 26
    length_live = 4
    length_vod = 3
    length_notes = 28
    # max 80
    length_all = 80

    build_path = "_build"
    if not path.exists(build_path):
        makedirs(build_path)

    final_list = []

    x = ""
    table_1 = "{0} {1} {2} {3} {4}".format(
        x.ljust(length_plugin_name, "="),
        x.ljust(length_domains, "="),
        x.ljust(length_live, "="),
        x.ljust(length_vod, "="),
        x.ljust(length_notes, "="),
    ).ljust(length_all)[:length_all]

    table_2 = "{0} {1} {2} {3} {4}".format(
        "Name".ljust(length_plugin_name, " "),
        "URL(s)".ljust(length_domains, " "),
        "Live".ljust(length_live, " "),
        "VOD".ljust(length_vod, " "),
        "GEO-Blocked - Notes".ljust(length_notes, " "),
    ).ljust(length_all)[:length_all]

    final_list.append(table_1)
    final_list.append(table_2)
    final_list.append(table_1)

    plugins_dict = create_dict_from_plugins()
    keys = sorted(list(plugins_dict.keys()))
    for key in keys:
        data = plugins_dict.get(key)

        # NAME
        plugin_name = "{0}".format(key).ljust(length_plugin_name)[:length_plugin_name]

        if data.get("broken"):
            continue

        # LIVE
        if data.get("live"):
            live_d = "Yes"
        else:
            live_d = "No"
        live = "{0}".format(live_d).ljust(length_live)[:length_live]

        # VOD
        if data.get("vod"):
            vod_d = "Yes"
        else:
            vod_d = "No"
        vod = "{0}".format(vod_d).ljust(length_vod)[:length_vod]

        # NOTES
        all_notes = []
        geo_blocked = data.get("geo_blocked")
        if geo_blocked:
            for country in sorted(geo_blocked):
                all_notes += ["{country}".format(country=country)]
        notes = data.get("notes")
        if notes:
            all_notes += [notes]

        if all_notes is not None:
            all_notes = " ".join(all_notes).ljust(length_notes)[:length_notes]

        # DOMAINS
        new_domains = []
        domains = data.get("domains")
        if domains:
            if len(domains) > 1:
                more_than_one = True
            else:
                more_than_one = False

            # FORMAT DOMAINS
            new_domains = []
            for domain in domains:
                if more_than_one:
                    new_domains += ["- {domain}".format(domain=domain).ljust(length_domains)[:length_domains]]
                else:
                    new_domains += ["{domain}".format(domain=domain).ljust(length_domains)[:length_domains]]
            new_domains = sorted(new_domains)

            # First domain
            first_line = "{plugin_name} {domain} {live} {vod} {notes}".format(
                plugin_name=plugin_name,
                domain=new_domains[0],
                live=live,
                vod=vod,
                notes=all_notes,
            ).ljust(length_all)[:length_all]
            final_list += [first_line]

            # other domains
            for domain in new_domains[1:]:
                next_line = "{0} {1}".format("".ljust(length_plugin_name)[:length_plugin_name], domain).ljust(length_all)[:length_all]
                final_list += [next_line]
        else:
            # No domains, just add the plugin_name.
            first_line = "{plugin_name}".format(plugin_name=plugin_name).ljust(length_all)[:length_all]
            final_list += [first_line]

    # End of list.
    final_list.append(table_1)
    # open file
    file_name = path.join(build_path, "plugin_matrix.txt")
    f = open(file_name, "w+")
    for x in final_list:
        f.write(x)
        f.write("\n")
    f.close()
    print("Done. plugin_matrix.txt")
