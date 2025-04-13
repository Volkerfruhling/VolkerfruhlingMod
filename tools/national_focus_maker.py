import yaml

def load_yaml():
    with open("tools/input/input.yaml", "r", encoding="utf-8") as file:
        yaml_data = yaml.safe_load(file)
    return yaml_data

def main():
    data = load_yaml()
    tree_name = f"focus_{data["focus_tree"]["country"]}"
    with open(f"tools/output/_vf_{tree_name}.txt", "w", encoding="utf-8") as file:
        file.write(
            f"#!gfx:interface\VF\goals\goals_{data["focus_tree"]["country"].lower()}.gfx\n"\
            f"focus_tree = {{\n"
            f"	id = {tree_name}\n"\
            f"	country = {{\n"\
            f"		factor = 0\n"\
            f"		modifier = {{\n"\
            f"			add = 10\n"\
            f"			tag = {data["focus_tree"]["country"]}\n"\
            f"		}}\n"\
            f"	}}\n"\
        )
        for focus in data["focus_tree"]["focuses"]:
            file.write(
                f"	# {focus["jp"]}\n"\
                f"	focus = {{\n"\
                f"		id = {tree_name}_{focus["tree"]}_{focus["id"]}\n"\
                f"		\n"\
                f"		# icon = GFX_goal_{tree_name}_{focus["id"]}\n"\
                f"		icon = GFX_goal_unknown\n"\
                f"		\n"\
                f"		cost = {focus["cost"]}\n"\
                f"		\n"\
                f"		x = {focus["x"]}\n"\
                f"		y = {focus["y"]}\n"\
                f"{relative_or_pre("relative",focus,tree_name)}"\
                f"{relative_or_pre("pre",focus,tree_name)}"\
                f"		available = {{\n"\
                f"			always = yes\n"\
                f"		}}\n"\
                f"		completion_reward = {{\n"\
                f"		}}\n"\
                f"		\n"\
                f"	}}\n"\
            )
        file.write(f"}}\n")

def relative_or_pre(which,focus,tree_name):
    if which == "relative" and "relative" in focus:
        return f"		relative_position_id = {tree_name}_{search_tree(focus["relative"])}_{focus["relative"]}\n"
    elif which == "pre" and "pre" in focus:
        pre = ""
        for pre_focus in focus["pre"]:
            pre += "		prerequisite = { # 前提NF\n"
            if type(pre_focus) == list:
                for pre_focus_id in pre_focus:
                    pre += f"			focus = {tree_name}_{search_tree(pre_focus_id)}_{pre_focus_id}\n"
            else:
                pre += f"			focus = {tree_name}_{search_tree(pre_focus)}_{pre_focus}\n"
            pre += "		}\n"
        return pre
    else:
        return ""
    
def search_tree(focusid, data = load_yaml()["focus_tree"]["focuses"]):
    for focus in data:
        if focus["id"] == focusid:
            return focus["tree"]
    return None

if __name__ == "__main__":
    main()