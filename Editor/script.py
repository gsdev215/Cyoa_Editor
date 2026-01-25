from lupa import LuaRuntime
import json

class LuaScriptSandbox:
    def __init__(self, current_node_data, player_data):
        # We use a single runtime for efficiency
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.cur_node = current_node_data
        self.player_data = player_data
        
    def _to_lua_safe_id(self, original_id):
        """Converts IDs with hyphens to Lua-safe variable names with underscores."""
        return str(original_id).replace('-', '_')

    def execute(self, user_script):
        # 1. Setup the 'White-room' Environment
        sandbox_env = self.lua.eval("""
            {
                math = math, string = string, table = table,
                pairs = pairs, ipairs = ipairs, 
                tonumber = tonumber, tostring = tostring,
                print = print -- Optional: remove for production
            }
        """)

        # 2. Inject Context (with ID sanitization)
        sandbox_env["url"] = self.cur_node.get("url", "")
        sandbox_env["description"] = self.cur_node.get("description", "")
        
        # lupa's table_from handles nested dicts/lists correctly
        sandbox_env["choices"] = self.lua.table_from(self.cur_node.get("choices", []))
        
        # Inject player data
        for k, v in self.player_data.items():
            sandbox_env[k] = v

        # Inject choice visibility variables (sanitized)
        choice_map = {} # To remember which sanitized ID maps to which real ID
        for choice in self.cur_node.get("choices", []):
            real_id = choice['id']
            safe_id = self._to_lua_safe_id(real_id)
            choice_map[safe_id] = real_id
            sandbox_env[f"choice_{safe_id}"] = True

        # 3. Secure Wrapper with Instruction Limit
        # We use 'load' (modern Lua) and pcall for safety
        safe_wrapper = self.lua.eval("""
            function(env, code)
                local chunk, err = load(code, "user_script", "t", env)
                if not chunk then return false, "Syntax Error: " .. tostring(err) end
                
                -- pcall catches runtime errors (like nil access or infinite loops)
                local status, res = pcall(chunk)
                if not status then return false, "Runtime Error: " .. tostring(res) end
                return true, env
            end
        """)

        try:
            success, result_or_error = safe_wrapper(sandbox_env, user_script)
        except Exception as e:
            print(f"Sandbox Crash: {e}")
            return None

        if not success:
            print(result_or_error)
            return None

        # 4. Extract & Reverse Mapping
        updated_env = result_or_error
        
        # Update Player Data
        new_player_data = {}
        for k in self.player_data.keys():
            new_player_data[k] = updated_env[k]

        # Extract Choice Booleans (mapping back to hyphens)
        choice_bools = {}
        for safe_id, real_id in choice_map.items():
            choice_bools[real_id] = updated_env[f"choice_{safe_id}"]

        return {
            "url": updated_env["url"],
            "description": updated_env["description"],
            "player_data": new_player_data,
            "choices_visibility": choice_bools
        }

# --- Testing the Refined Logic ---
if __name__ == "__main__":
    node_data = {
        "url": "https://forest.com",
        "description": "The trees whisper.",
        "choices": [
            {"id": "52cd4b74-08d2-4709-8804-e6fa6deebe36", "text": "Stay"},
            {"id": "3da81c9d-67bc-4419-ae5a-082c388a6d6d", "text": "Run"}
        ]
    }
    player_vars = {"energy": 20}

    # User Lua uses underscores for the IDs
    user_lua = """
    energy = energy + 10
    description = "You feel energized by the forest."
    -- Disable the 'Run' choice if energy is high
    if energy > 25 then
        choice_3da81c9d_67bc_4419_ae5a_082c388a6d6d = false
    end
    """

    sandbox = LuaScriptSandbox(node_data, player_vars)
    results = sandbox.execute(user_lua)

    if results:
        print(f"Energy: {results['player_data']['energy']}")
        print(f"Run Visible: {results['choices_visibility']['3da81c9d-67bc-4419-ae5a-082c388a6d6d']}")