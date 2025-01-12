import os

class ModManagerSearch:
    def __init__(self, mod_directory):
        self.mod_directory = mod_directory

    def search_mods(self, query):
        """Search for mods by name, description, or Steam Workshop ID."""
        results = []
        query_lower = query.lower()

        if not os.path.exists(self.mod_directory):
            return results

        # Search by mod name, description in mod.info, or workshop ID in mod.json
        for mod_name in os.listdir(self.mod_directory):
            mod_path = os.path.join(self.mod_directory, mod_name)
            if os.path.isdir(mod_path):
                mod_info_path = os.path.join(mod_path, 'mod.info')
                mod_json_path = os.path.join(mod_path, 'mod.json')

                # Check if mod.info exists for description search
                if os.path.isfile(mod_info_path):
                    with open(mod_info_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        if query_lower in mod_name.lower() or query_lower in content:
                            results.append(mod_name)
                else:
                    # Check if mod.json exists for workshop ID search
                    if os.path.isfile(mod_json_path):
                        with open(mod_json_path, 'r', encoding='utf-8', errors='ignore') as f:
                            try:
                                import json
                                mod_data = json.load(f)
                                if 'workshop_id' in mod_data and query_lower in str(mod_data['workshop_id']).lower():
                                    results.append(mod_name)
                            except json.JSONDecodeError:
                                pass

                    # Check if query matches mod name
                    if query_lower in mod_name.lower():
                        results.append(mod_name)

        return results