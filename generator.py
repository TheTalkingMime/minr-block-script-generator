import requests, json
import pandas as pd
import warnings
import os

warnings.filterwarnings('ignore')

def main(world):
    filename = f"{world}_coords.csv"
    if not os.path.exists(filename):
        print(f"No {filename} detected")
        return
    df = pd.read_csv(filename)

    coord_mappings = {
        "north (-z)": (2, -1),
        "south (+z)": (2, 1),
        "east (+x)": (0, 1),
        "west (-x)": (0, -1),
        "above": (1, 1),
        "below": (1, -1),
    }

    data = pd.DataFrame(columns=df.columns)
    final_script = ""
    for _, row in df.iterrows():
        if row.isna().all():
            continue
        if pd.isnull(row['x']) or pd.isnull(row['y']) or pd.isnull(row['z']):
            if pd.isnull(row['f3i']):
                print(f"Invalid row detected, no coords or f3i provided\n{row}")
                continue
            else:
                row["x"], row["y"], row["z"] = parse_f3i(row["f3i"])

        if pd.isnull(row['delay']):
            row['delay'] = 5
        
        if pd.isnull(row['cooldown']):
            row['cooldown'] = 5

        if pd.isnull(row['link']):
            row['link'] = build_block_script(row, coord_mappings, world)

        
            
        final_script += (
            f"@bypass /s i i {int(row['x'])} {int(row['y'])} {int(row['z'])}{' Theta ' if world == 'theta' else ' '}{row['link']}\n"
        )
        data = data.append(row)

    data.to_csv(filename, index=False)
    print(f"{world}: {build_link(final_script)}")


def build_block_script(row, coord_mappings, world):
    script = (
        "@fast\n"
        f"@global_cooldown {int(row['cooldown'])}\n"
        f"@delay {int(row['delay'])}"
    )

    for direction in coord_mappings:
        if pd.isnull(row[direction]):
            continue
        coord, d = coord_mappings[direction]
        deltas = [0, 0, 0]
        deltas[coord] += d
        script += f"\n@bypass /execute in minecraft:{world} run setblock {int(row['x'] + deltas[0])} {int(row['y'] + deltas[1])} {int(row['z'] + deltas[2])} air"
    return build_link(script)


def parse_f3i(f3i_string):
    _, x, y, z = f3i_string.split(" ")[0:4]
    return int(x), int(y), int(z)


def build_link(data):
    url_id = json.loads(
        requests.post("https://paste.minr.org/documents", data=data).content
    )["key"]
    return f"https://paste.minr.org/{url_id}.coffeescript"





for world in ["overworld", "theta"]: 
    main(world)
input()
