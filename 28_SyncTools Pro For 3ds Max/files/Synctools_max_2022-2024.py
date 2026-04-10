# -*- coding: utf-8 -*-
import os
import sys
import re
import hashlib
from pathlib import Path
from pymxs import runtime as rt

class CopyPaste3dsMax:
    """
    用于在3ds MAX中实现对象的复制粘贴功能。
    可以将选中的对象导出到临时文件夹,方便在不同软件或场景间传递。
    """

    def __init__(self):
        # 设置缓存目录路径
        # Use AppData for potentially better cross-machine/user compatibility if roaming profiles are used
        # app_data = rt.pathConfig.getDir(rt.name('userScripts')) # Example alternative path
        self.dirpath = os.path.join(os.path.expanduser("~"), "Documents", "Cache") # Changed name slightly
        if not os.path.exists(self.dirpath):
            try:
                os.makedirs(self.dirpath)
                print(f"缓存目录已创建: {self.dirpath}")
            except OSError as e:
                print(f"创建缓存目录失败: {self.dirpath}, 错误: {e}")
                # Fallback or raise error? For now, print and continue, operations might fail.
                self.dirpath = None # Indicate failure

        self.counter_file = os.path.join(self.dirpath, "export_counter.txt") if self.dirpath else None
        self.hierarchy_file = os.path.join(self.dirpath, "hierarchy.txt") if self.dirpath else None
        self.max_exports = 10 # Maximum number of export files before cleanup

    def get_unique_name(self, name, name_dict):
        """为对象获取唯一名称,如果名称已存在则添加数字。"""
        # Ensure name is a string, handle potential None or non-string types
        name_str = str(name) if name is not None else "UnnamedNode"
        # Sanitize name for file system or other uses if necessary (e.g., remove invalid chars)
        # base_name = re.sub(r'[^\w\.-]', '_', name_str) # Example sanitization
        base_name = re.sub(r'\.\d+$', '', name_str) # Keep original logic for now

        if base_name not in name_dict:
            name_dict[base_name] = 0 # Start count at 0, first use is base_name
            return base_name
        else:
            name_dict[base_name] += 1
            # Keep incrementing until a unique name is found
            while True:
                unique_name = f"{base_name}.{name_dict[base_name]:03d}"
                # Check if this generated name *also* exists as a base name (less likely but possible)
                if unique_name not in name_dict:
                     # Optional: Add the generated name to dict to prevent future collisions if needed
                     # name_dict[unique_name] = 0
                     return unique_name
                name_dict[base_name] += 1


    def write_hierarchy_to_file(self, node, level=0, file=None, name_dict=None):
        """递归写入选中对象的层级结构到文件。"""
        if node is None or file is None or name_dict is None:
            return

        try:
            # Use node.name which should be available
            unique_name = self.get_unique_name(node.name, name_dict)
            indent = ' ' * level * 4
            file.write(f"{indent}{unique_name} (Class: {rt.classOf(node)})\n") # Added class info

            # Recursively process children
            for child in node.children:
                self.write_hierarchy_to_file(child, level + 1, file, name_dict)
        except Exception as e:
            print(f"写入层级时出错: 对象 '{node.name if node else 'None'}', 错误: {e}")


    def get_export_counter(self):
        """获取当前导出计数。"""
        if not self.counter_file or not os.path.exists(self.counter_file):
            return 1
        try:
            with open(self.counter_file, 'r') as file:
                content = file.read().strip()
                if content.isdigit():
                    return int(content)
                else:
                    print(f"计数文件内容无效: {content}. 重置为 1.")
                    return 1 # Reset if content is invalid
        except Exception as e:
            print(f"读取计数文件失败: {e}. 重置为 1.")
            return 1

    def set_export_counter(self, counter):
        """设置导出计数。"""
        if not self.counter_file:
            print("错误: 计数文件路径未设置。")
            return
        try:
            with open(self.counter_file, 'w') as file:
                file.write(str(counter))
        except Exception as e:
            print(f"写入计数文件失败: {e}")


    def delete_previous_exports(self):
        """删除之前的导出文件。"""
        if not self.dirpath or not os.path.exists(self.dirpath):
            print("缓存目录不存在，无法删除文件。")
            return

        deleted_count = 0
        for filename in os.listdir(self.dirpath):
            # More specific pattern matching
            if re.match(r"export_\d+\.fbx", filename):
                try:
                    os.remove(os.path.join(self.dirpath, filename))
                    deleted_count += 1
                except OSError as e:
                    print(f"删除文件失败: {filename}, 错误: {e}")

        if deleted_count > 0:
            print(f"已删除 {deleted_count} 个之前的导出文件。")
        else:
            print("未找到需要删除的旧导出文件。")

    def max_copy(self):
        """导出选中对象为FBX。"""
        if not self.dirpath:
             print("错误: 缓存目录未初始化，无法导出。")
             return

        # 检查是否有选中的对象
        current_selection = rt.getCurrentSelection() # Use getCurrentSelection for safety
        if len(current_selection) == 0: # Check length
            rt.messageBox("未选择对象。\n请至少选择一个对象后重试。", title="SyncTools 提示")
            print("未选择对象。")
            return

        counter = self.get_export_counter()

        # 达到 N 时重置并清理
        if counter > self.max_exports: # Use > instead of >= for clarity
            print(f"导出计数达到 {self.max_exports}, 清理旧文件...")
            self.delete_previous_exports()
            counter = 1 # Reset counter
            self.set_export_counter(counter) # Save reset counter

        export_filename = f"export_{counter}.fbx"
        export_path = os.path.join(self.dirpath, export_filename)

        # --- FBX Export Options ---
        # It's crucial to configure FBX options for reliable export.
        # Using 'noPrompt' might use default/last used settings, which can vary.
        # Example: Explicitly set some common options using MaxScript commands via rt.execute
        try:
            print("正在配置 FBX 导出选项...")
            rt.FBXExporterSetParam("Animation", False) # Example: Disable animation export
            rt.FBXExporterSetParam("Cameras", False)   # Example: Disable camera export
            rt.FBXExporterSetParam("Lights", False)    # Example: Disable light export
            rt.FBXExporterSetParam("EmbedMedia", False)# Example: Don't embed textures
            rt.FBXExporterSetParam("UpAxis", "Y")      # Example: Set Y-up axis
            # Add more options as needed based on FBX Exporter documentation
            print("FBX 导出选项配置完成。")

            # --- Perform Export ---
            print(f"正在导出到: {export_path}")
            # Use keyword arguments directly if pymxs supports them for exportFile, otherwise stick to name("noPrompt")
            # Check pymxs documentation for exportFile specifics. Assuming name("noPrompt") is safer.
            export_success = rt.exportFile(export_path, rt.name("noPrompt"), selectedOnly=True)

            if export_success: # Check return value if possible (exportFile might return bool or status)
                 print(f"FBX 导出成功: {export_path}")
                 self.set_export_counter(counter + 1) # Increment counter only on success

                 # --- Save Hierarchy ---
                 if not self.hierarchy_file:
                      print("错误: 层级文件路径未设置，无法保存层级。")
                      return

                 print(f"正在保存层级结构到: {self.hierarchy_file}")
                 try:
                     with open(self.hierarchy_file, 'w', encoding='utf-8') as file:
                         name_dict = {} # Reset name dict for each export
                         # Iterate through top-level selected nodes only
                         top_level_nodes = [obj for obj in current_selection if obj.parent is None or obj.parent not in current_selection]
                         if not top_level_nodes: # If selection is entirely children of other selected nodes
                             top_level_nodes = current_selection # Fallback to writing all selected

                         for obj in top_level_nodes:
                             self.write_hierarchy_to_file(obj, 0, file, name_dict)
                     print(f"层级结构已保存。")
                 except Exception as e:
                     print(f"保存层级结构失败: {str(e)}")
            else:
                 # exportFile might not return a useful status, rely on exceptions or check file existence
                 if not os.path.exists(export_path):
                      print(f"导出失败: 文件未创建 {export_path}")
                      rt.messageBox(f"导出失败: 文件未创建。\n检查日志获取详情。", title="SyncTools 错误")
                 else:
                      # File might exist but be invalid/empty
                      print(f"导出完成，但可能存在问题 (检查文件): {export_path}")
                      # Increment counter even if export might have issues? Depends on desired behavior.
                      self.set_export_counter(counter + 1)


        except Exception as e:
            # Catch potential exceptions during export or hierarchy writing
            print(f"导出过程中发生错误: {str(e)}")
            # Provide more specific feedback if possible
            import traceback
            traceback.print_exc() # Print detailed traceback to console/listener
            rt.messageBox(f"导出过程中发生错误:\n{e}\n\n检查 MaxScript 监听器获取详细信息。", title="SyncTools 错误")


    def max_paste(self):
        """从缓存目录导入最新的FBX文件。"""
        if not self.dirpath:
             print("错误: 缓存目录未初始化，无法导入。")
             return

        latest_fbx = self.get_latest_fbx_file()
        if latest_fbx is None:
            rt.messageBox("缓存目录中没有找到可导入的 FBX 文件。", title="SyncTools 提示")
            return

        try:
            # --- FBX Import Options ---
            # Similar to export, configure import options if needed
            print("正在配置 FBX 导入选项...")
            # Example: Set import mode to "add" (don't merge with scene)
            rt.FBXImporterSetParam("ImportMode", rt.name("add"))
            # Example: Ensure materials are imported
            rt.FBXImporterSetParam("Materials", True)
            # Add more options as needed
            print("FBX 导入选项配置完成。")

            print(f"正在导入: {latest_fbx}")
            # Use str() to ensure path is passed correctly
            import_success = rt.importFile(str(latest_fbx), rt.name("noPrompt"), clearScene=False) # Ensure scene isn't cleared

            if import_success: # Check return value if possible
                print(f"成功导入: {latest_fbx}")
                rt.messageBox(f"已成功导入:\n{os.path.basename(str(latest_fbx))}", title="SyncTools 成功")

                # --- Optional: Delete after import ---
                # Consider making this configurable or asking the user
                delete_after_import = False # Default to not deleting
                if delete_after_import:
                    try:
                        os.remove(str(latest_fbx))
                        print(f"已删除导入的文件: {latest_fbx}")
                    except Exception as e:
                        print(f"删除导入的文件失败: {e}")
                else:
                     print(f"保留导入的文件: {latest_fbx}")

            else:
                # importFile might not return a useful status, rely on exceptions
                print(f"导入可能失败或无内容导入: {latest_fbx}")
                # Check if new objects were actually added to the scene if possible
                rt.messageBox(f"导入操作完成，但可能未成功导入任何对象。\n文件: {os.path.basename(str(latest_fbx))}", title="SyncTools 警告")

        except Exception as e:
            print(f"导入失败: {str(e)}")
            import traceback
            traceback.print_exc()
            rt.messageBox(f"导入失败:\n{e}\n\n检查 MaxScript 监听器获取详细信息。", title="SyncTools 错误")

    def get_latest_fbx_file(self):
        """获取缓存目录中最新的FBX文件。"""
        if not self.dirpath or not os.path.exists(self.dirpath):
            print("缓存目录不存在。")
            return None

        try:
            fbx_files = list(Path(self.dirpath).glob("export_*.fbx"))
            if not fbx_files:
                print("缓存目录中未找到 'export_*.fbx' 文件。")
                return None

            # Find the file with the highest number in its name, assuming format export_N.fbx
            latest_file = None
            max_num = -1
            for f in fbx_files:
                match = re.search(r"export_(\d+)\.fbx", f.name)
                if match:
                    num = int(match.group(1))
                    if num > max_num:
                        max_num = num
                        latest_file = f

            # Fallback to modification time if numbering scheme fails or isn't strict
            if latest_file is None and fbx_files:
                 print("无法从文件名确定最新文件，将使用修改时间。")
                 latest_file = max(fbx_files, key=lambda p: p.stat().st_mtime)


            if latest_file:
                 print(f"找到最新文件: {latest_file}")
                 return latest_file
            else:
                 print("未找到有效的 FBX 文件。")
                 return None

        except Exception as e:
            print(f"查找最新 FBX 文件时出错: {e}")
            return None


# --- Global Instance ---
# Create instance once when script is loaded.
# Be mindful of state if Max is kept open and script is re-run.
g_copy_paste_instance = CopyPaste3dsMax()

# --- Functions exposed to MaxScript ---
# These need to be defined globally or made accessible
# so rt.execute can find them.

def executeCopy():
    """Wrapper function called by MaxScript macro for Copy."""
    global g_copy_paste_instance
    if g_copy_paste_instance:
        try:
            g_copy_paste_instance.max_copy()
        except Exception as e:
            print(f"执行复制时出错: {e}")
            import traceback
            traceback.print_exc()
            rt.messageBox(f"执行复制时出错:\n{e}", title="SyncTools 错误")
    else:
        print("错误: SyncTools 未初始化。")
        rt.messageBox("错误: SyncTools 未初始化。", title="SyncTools 错误")


def executePaste():
    """Wrapper function called by MaxScript macro for Paste."""
    global g_copy_paste_instance
    if g_copy_paste_instance:
        try:
            g_copy_paste_instance.max_paste()
        except Exception as e:
            print(f"执行粘贴时出错: {e}")
            import traceback
            traceback.print_exc()
            rt.messageBox(f"执行粘贴时出错:\n{e}", title="SyncTools 错误")
    else:
        print("错误: SyncTools 未初始化。")
        rt.messageBox("错误: SyncTools 未初始化。", title="SyncTools 错误")

# --- Expose Python functions to MaxScript Runtime ---
# This allows calling them via python.execute("...") in MaxScript
rt.executeCopy = executeCopy
rt.executePaste = executePaste


def create_menu():
    """创建或更新 3ds Max 菜单项。"""
    print("正在尝试创建 Sync Tools 菜单...")

    # --- Define the Macro Scripts ---
    # These link UI elements (like menu items) to MaxScript commands.
    # The MaxScript commands will call our Python functions via python.execute().
    macro_category = "SyncTools"
    copy_macro_name = "SyncToolsCopy"
    paste_macro_name = "SyncToolsPaste"

    try:
        rt.macros.new(
            macro_category,
            copy_macro_name,
            "复制选中对象到缓存 (SyncTools)", # Tooltip
            "Copy",                     # Menu display text / Button text
            'python.execute("executeCopy()")' # MaxScript code to execute
        )
        print(f"宏脚本 '{copy_macro_name}' 已创建或更新。")

        rt.macros.new(
            macro_category,
            paste_macro_name,
            "从缓存粘贴最新对象 (SyncTools)", # Tooltip
            "Paste",                    # Menu display text / Button text
            'python.execute("executePaste()")' # MaxScript code to execute
        )
        print(f"宏脚本 '{paste_macro_name}' 已创建或更新。")

    except Exception as e:
        print(f"创建宏脚本时出错: {e}")
        rt.messageBox(f"创建宏脚本时出错:\n{e}", title="SyncTools 错误")
        return # Stop if macros can't be created

    # --- Build the Menu using MaxScript executed from Python ---
    menu_title = "Sync Tools" # The name visible in the main menu bar

    # MaxScript code to create/update the menu
    # Uses menuMan interface for better control
    mxs_code = f"""
    (
        -- Function to find or create a submenu
        fn findOrCreateSubMenu menuName parentMenu =
        (
            local existingMenu = undefined
            -- Check if menu already exists
            for i = 1 to (parentMenu.numItems()) do
            (
                local item = parentMenu.getItem i
                if item.getTitle() == menuName then
                (
                    existingMenu = item.getSubMenu()
                    exit
                )
            )

            if existingMenu == undefined then
            (
                -- Create the submenu if it doesn't exist
                local newSubMenu = menuMan.createMenu menuName
                local newMenuItem = menuMan.createSubMenuItem menuName newSubMenu
                parentMenu.addItem newMenuItem -1 -- Add to end
                format "创建子菜单: '%'.\\n" menuName
                newSubMenu -- Return the newly created submenu
            )
            else
            (
                 format "找到现有子菜单: '%'.\\n" menuName
                 existingMenu -- Return the existing submenu
            )
        )

        -- Function to add an action item if it doesn't exist
        fn addActionItemIfNotExists actionItem title targetMenu =
        (
            local itemExists = false
            for i = 1 to (targetMenu.numItems()) do
            (
                local item = targetMenu.getItem i
                if item.getTitle() == title then
                (
                    itemExists = true
                    exit
                )
            )

            if not itemExists then
            (
                targetMenu.addItem actionItem -1 -- Add to end
                format "添加菜单项: '%' 到菜单 '%'.\\n" title targetMenu.getTitle()
            )
            else
            (
                 format "菜单项 '%' 已存在于菜单 '%' 中.\\n" title targetMenu.getTitle()
            )
        )

        -- Get the main menu bar
        local mainMenuBar = menuMan.getMainMenuBar()
        if mainMenuBar == undefined then
        (
            messageBox "无法获取主菜单栏。" title:"SyncTools 错误"
            return false -- Indicate failure
        )

        -- Find or create the "Sync Tools" submenu
        local syncToolsSubMenu = findOrCreateSubMenu "{menu_title}" mainMenuBar

        if syncToolsSubMenu == undefined then
        (
             messageBox "无法创建或找到 'Sync Tools' 子菜单。" title:"SyncTools 错误"
             return false -- Indicate failure
        )

        -- Create action items linked to the macros
        -- Format is "MacroName`Category"
        local copyAction = menuMan.createActionItem "{copy_macro_name}" "{macro_category}"
        local pasteAction = menuMan.createActionItem "{paste_macro_name}" "{macro_category}"

        -- Add actions to the submenu, ensuring no duplicates
        addActionItemIfNotExists copyAction "Copy" syncToolsSubMenu
        addActionItemIfNotExists pasteAction "Paste" syncToolsSubMenu

        -- Update the menu bar to reflect changes
        menuMan.updateMenuBar()
        format "'{menu_title}' 菜单已创建或更新。\\n"

        true -- Indicate success
    )
    """
    # Execute the MaxScript code
    try:
        print("正在执行 MaxScript 以创建/更新菜单...")
        success = rt.execute(mxs_code)
        if success:
            print("菜单创建/更新脚本执行成功。")
        else:
            print("菜单创建/更新脚本执行失败或未执行任何操作 (可能已存在)。")
    except Exception as e:
        print(f"执行 MaxScript 菜单代码时出错: {e}")
        import traceback
        traceback.print_exc()
        rt.messageBox(f"创建菜单时发生 MaxScript 错误:\n{e}\n\n检查监听器获取详细信息。", title="SyncTools 错误")


def main():
    """主入口点，创建菜单。"""
    # Ensure instance is created (it's global now, but good practice)
    global g_copy_paste_instance
    if g_copy_paste_instance is None:
        g_copy_paste_instance = CopyPaste3dsMax()

    create_menu()
    print("SyncTools_max.py 脚本执行完毕。")
    # Optional: Display a message box confirming setup
    # rt.messageBox("Sync Tools 菜单已加载。", title="SyncTools")

if __name__ == "__main__":
    # This block typically runs when the script is executed directly.
    # In Max, scripts are often run via 'Run Script' or placed in startup folders.
    main()
