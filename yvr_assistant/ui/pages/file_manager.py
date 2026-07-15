"""
YVR助手 - 文件管理页面
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from ui.theme import COLORS, FONTS


class FileManagerPage(ctk.CTkFrame):
    """文件管理页面 - 设备文件浏览与管理"""

    def __init__(self, master, adb_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.adb = adb_manager
        self._current_path = "/sdcard/"
        self._files = []
        self._file_items = []
        self._build()

    def _build(self):
        # 标题栏
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 10))

        ctk.CTkLabel(
            header, text="文件管理", font=FONTS["title"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="管理设备存储文件",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(15, 0))

        # 提示
        self.tip_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        self.tip_frame.pack(fill="x", padx=30, pady=(0, 10))

        self.tip_label = ctk.CTkLabel(
            self.tip_frame,
            text="⚠️ 请先连接设备后再使用文件管理",
            font=FONTS["body"],
            text_color=COLORS["warning"],
        )
        self.tip_label.pack(pady=12)

        # 路径导航栏
        nav_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        nav_frame.pack(fill="x", padx=30, pady=(0, 10))

        self.back_btn = ctk.CTkButton(
            nav_frame, text="⬅ 返回上级", font=FONTS["small"],
            fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
            corner_radius=6, width=90, height=30,
            command=self._go_back
        )
        self.back_btn.pack(side="left", padx=(10, 10), pady=10)

        self.path_label = ctk.CTkLabel(
            nav_frame, text="/sdcard/", font=FONTS["mono"],
            text_color=COLORS["text_primary"]
        )
        self.path_label.pack(side="left", pady=10)

        self.refresh_btn = ctk.CTkButton(
            nav_frame, text="刷新", font=FONTS["small"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_dark"],
            corner_radius=6, width=60, height=30,
            command=self._refresh_files
        )
        self.refresh_btn.pack(side="right", padx=(0, 10), pady=10)

        # 操作按钮栏
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=30, pady=(0, 5))

        actions = [
            ("📤 上传文件", self._upload_file),
            ("📥 下载选中", self._download_selected),
            ("📁 新建文件夹", self._new_folder),
            ("🗑️ 删除选中", self._delete_selected),
        ]
        for text, cmd in actions:
            btn = ctk.CTkButton(
                action_frame, text=text, font=FONTS["small"],
                fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"],
                corner_radius=6, height=30,
                command=cmd
            )
            btn.pack(side="left", padx=(0, 8))

        # 文件列表
        self.file_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["border_light"],
            scrollbar_button_hover_color=COLORS["text_muted"],
        )
        self.file_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self._selected = set()

    def _parse_ls_output(self, output):
        """解析 ls -la 输出"""
        files = []
        for line in output.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith("total"):
                continue
            # 跳过 . 和 .. (但保留它们用于导航)
            parts = line.split()
            if len(parts) < 6:
                continue
            # 检查是否是 . 或 ..
            name = ' '.join(parts[5:])
            is_dir = parts[0].startswith('d')
            files.append({"name": name, "is_dir": is_dir, "raw": line})
        return files

    def _refresh_files(self):
        if not self.adb.is_connected:
            self.tip_label.configure(text="⚠️ 请先连接设备！")
            return

        self.path_label.configure(text=self._current_path)

        def on_result(code, out, err):
            self.after(0, lambda: self._on_files_result(code, out, err))

        self.adb.list_files(self._current_path, on_result)

    def _on_files_result(self, code, out, err):
        if code != 0:
            self.tip_label.configure(text=f"❌ 读取目录失败: {err}")
            return

        self._files = self._parse_ls_output(out)
        self._selected.clear()
        self._render_file_list()

    def _render_file_list(self):
        """渲染文件列表"""
        for item in self._file_items:
            item.destroy()
        self._file_items.clear()

        if not self._files:
            empty = ctk.CTkLabel(
                self.file_container, text="此目录为空",
                font=FONTS["body"], text_color=COLORS["text_muted"]
            )
            empty.pack(pady=30)
            self._file_items.append(empty)
            return

        # 表头
        header = ctk.CTkFrame(self.file_container, fg_color=COLORS["bg_card"], corner_radius=8)
        header.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(
            header, text="  文件名", font=FONTS["small"],
            text_color=COLORS["text_muted"], width=300
        ).pack(side="left", padx=5, pady=6)
        ctk.CTkLabel(
            header, text="类型", font=FONTS["small"],
            text_color=COLORS["text_muted"], width=70
        ).pack(side="left", padx=5, pady=6)
        self._file_items.append(header)

        for f in self._files:
            if f["name"] in (".", ".."):
                continue

            item_frame = ctk.CTkFrame(
                self.file_container, fg_color=COLORS["bg_card"], corner_radius=8
            )
            item_frame.pack(fill="x", pady=(0, 3))

            icon = "📁" if f["is_dir"] else "📄"
            name_label = ctk.CTkLabel(
                item_frame,
                text=f"  {icon}  {f['name']}",
                font=FONTS["body"],
                text_color=COLORS["text_primary"],
                anchor="w"
            )
            name_label.pack(side="left", fill="x", expand=True, padx=5, pady=8)

            type_label = ctk.CTkLabel(
                item_frame,
                text="文件夹" if f["is_dir"] else "文件",
                font=FONTS["small"],
                text_color=COLORS["text_secondary"],
                width=70
            )
            type_label.pack(side="left", padx=5, pady=8)

            # 点击事件
            name_label.bind("<Button-1>", lambda e, f=f: self._on_item_click(f))
            item_frame.bind("<Button-1>", lambda e, f=f: self._on_item_click(f))

            # 右键菜单标记选中
            name_label.bind("<Button-3>", lambda e, f=f: self._toggle_select(f))
            item_frame.bind("<Button-3>", lambda e, f=f: self._toggle_select(f))

            item_frame._file_data = f
            item_frame._name_label = name_label
            self._file_items.append(item_frame)

    def _on_item_click(self, file_data):
        if file_data["is_dir"]:
            if file_data["name"] == ".":
                return
            elif file_data["name"] == "..":
                self._go_back()
            else:
                self._current_path = self._current_path.rstrip("/") + "/" + file_data["name"] + "/"
                self._refresh_files()

    def _toggle_select(self, file_data):
        name = file_data["name"]
        if name in self._selected:
            self._selected.discard(name)
        else:
            self._selected.add(name)
        self._update_selection_highlight()

    def _update_selection_highlight(self):
        for item in self._file_items:
            if hasattr(item, "_file_data"):
                name = item._file_data["name"]
                if name in self._selected:
                    item.configure(fg_color=COLORS["accent_dark"])
                else:
                    item.configure(fg_color=COLORS["bg_card"])

    def _go_back(self):
        if self._current_path in ("/", "/sdcard"):
            return
        parts = self._current_path.rstrip("/").split("/")
        parts.pop()
        self._current_path = "/".join(parts) + "/"
        self._refresh_files()

    def _upload_file(self):
        if not self.adb.is_connected:
            self.tip_label.configure(text="⚠️ 请先连接设备！")
            return

        files = filedialog.askopenfilenames(title="选择要上传的文件")
        for f in files:
            remote = self._current_path.rstrip("/") + "/" + os.path.basename(f)

            def on_done(code, out, err):
                self.after(0, lambda: self._on_upload_done(code, out, err))

            self.adb.push_file(f, remote, on_done)

    def _on_upload_done(self, code, out, err):
        if code == 0:
            self.tip_label.configure(text="✅ 文件上传成功")
            self._refresh_files()
        else:
            self.tip_label.configure(text=f"❌ 上传失败: {err}")

    def _download_selected(self):
        if not self.adb.is_connected:
            self.tip_label.configure(text="⚠️ 请先连接设备！")
            return
        if not self._selected:
            messagebox.showinfo("提示", "请先在文件上右键选择要下载的文件")
            return

        local_dir = filedialog.askdirectory(title="选择下载保存目录")
        if not local_dir:
            return

        for name in self._selected:
            remote = self._current_path.rstrip("/") + "/" + name
            local = os.path.join(local_dir, name)

            def on_done(code, out, err, n=name):
                self.after(0, lambda: self._on_download_done(code, out, err, n))

            self.adb.pull_file(remote, local, on_done)

    def _on_download_done(self, code, out, err, name):
        if code == 0:
            self.tip_label.configure(text=f"✅ {name} 下载成功")
        else:
            self.tip_label.configure(text=f"❌ 下载 {name} 失败: {err}")

    def _new_folder(self):
        if not self.adb.is_connected:
            self.tip_label.configure(text="⚠️ 请先连接设备！")
            return

        dialog = ctk.CTkInputDialog(
            text="请输入文件夹名称:", title="新建文件夹"
        )
        name = dialog.get_input()
        if name:
            remote = self._current_path.rstrip("/") + "/" + name

            def on_done(code, out, err):
                self.after(0, lambda: self._refresh_files())

            self.adb.mkdir(remote, on_done)

    def _delete_selected(self):
        if not self.adb.is_connected:
            self.tip_label.configure(text="⚠️ 请先连接设备！")
            return
        if not self._selected:
            messagebox.showinfo("提示", "请先在文件上右键选择要删除的文件")
            return

        if not messagebox.askyesno("确认删除", f"确定要删除选中的 {len(self._selected)} 个文件/文件夹吗？"):
            return

        for name in self._selected:
            remote = self._current_path.rstrip("/") + "/" + name
            self.adb.delete_file(remote)

        self._selected.clear()
        self.after(500, self._refresh_files)

    def on_show(self):
        if self.adb.is_connected:
            self.tip_label.configure(text=f"✅ 设备已连接 - 当前路径: {self._current_path}")
            self._refresh_files()
        else:
            self.tip_label.configure(text="⚠️ 请先连接设备后再使用文件管理")