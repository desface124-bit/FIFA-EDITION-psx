import os
import shutil
from pathlib import Path

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.popup import Popup
from kivy.storage.jsonstore import JsonStore


class PlayerList(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = "PlayerRow"
        self.layout_manager = RecycleBoxLayout(
            default_size=(None, dp(54)),
            default_size_hint=(1, None),
            size_hint_y=None,
            orientation="vertical",
        )
        self.layout_manager.bind(minimum_height=self.layout_manager.setter("height"))


class PlayerRow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(54)
        self.spacing = dp(4)
        self.padding = dp(4)

        self.lbl_id = Label(size_hint_x=.12)
        self.lbl_name = Label(size_hint_x=.30, halign="left")
        self.lbl_last = Label(size_hint_x=.30, halign="left")
        self.lbl_offset = Label(size_hint_x=.18, font_size="11sp")
        self.lbl_len = Label(size_hint_x=.10, font_size="11sp")

        for w in (self.lbl_name, self.lbl_last):
            w.bind(size=lambda inst, val: setattr(inst, "text_size", (inst.width, None)))

        self.add_widget(self.lbl_id)
        self.add_widget(self.lbl_name)
        self.add_widget(self.lbl_last)
        self.add_widget(self.lbl_offset)
        self.add_widget(self.lbl_len)

    def refresh_view_attrs(self, rv, index, data):
        result = super().refresh_view_attrs(rv, index, data)
        self.lbl_id.text = str(data.get("id", ""))
        self.lbl_name.text = data.get("first", "")
        self.lbl_last.text = data.get("last", "")
        self.lbl_offset.text = data.get("offset_hex", "")
        self.lbl_len.text = str(data.get("max_bytes", ""))
        return result

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.is_double_tap:
            app = App.get_running_app()
            app.select_player_by_id(self.lbl_id.text)
            return True
        return super().on_touch_down(touch)


class FIFA2001AndroidEditor(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bin_path = None
        self.player_records = []
        self.filtered_indices = []
        self.selected_index = None
        self.store = JsonStore(os.path.join(self.user_data_dir, "settings.json"))

    def build(self):
        self.title = "FIFA 2001 Player Editor"

        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(6))

        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(6))
        self.open_btn = Button(text="📂 Abrir arquivo", size_hint_x=.35)
        self.open_btn.bind(on_release=self.open_file)
        top.add_widget(self.open_btn)

        self.status = Label(
            text="Nenhum arquivo aberto.",
            halign="left",
            valign="middle",
            size_hint_x=.65,
        )
        self.status.bind(size=lambda inst, val: setattr(inst, "text_size", (inst.width, None)))
        top.add_widget(self.status)
        root.add_widget(top)

        search = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        search.add_widget(Label(text="🔎", size_hint_x=.08))
        self.search = TextInput(
            hint_text="Buscar jogador...",
            multiline=False,
            size_hint_x=.92,
        )
        self.search.bind(text=self.filter_players)
        search.add_widget(self.search)
        root.add_widget(search)

        header = GridLayout(cols=5, size_hint_y=None, height=dp(34))
        for text in ("#", "Nome", "Sobrenome", "Offset", "Bytes"):
            header.add_widget(Label(text=text, bold=True))
        root.add_widget(header)

        self.list = PlayerList()
        root.add_widget(self.list)

        edit = GridLayout(cols=2, size_hint_y=None, height=dp(150), spacing=dp(5))

        edit.add_widget(Label(text="Nome:"))
        self.first_input = TextInput(multiline=False)
        edit.add_widget(self.first_input)

        edit.add_widget(Label(text="Sobrenome / Apelido:"))
        self.last_input = TextInput(multiline=False)
        edit.add_widget(self.last_input)

        self.bytes_info = Label(text="Bytes: 0/0")
        edit.add_widget(self.bytes_info)

        self.save_btn = Button(text="💾 Salvar no arquivo", disabled=True)
        self.save_btn.bind(on_release=self.save_player_directly)
        edit.add_widget(self.save_btn)

        root.add_widget(edit)

        bottom = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        backup_btn = Button(text="Criar backup")
        backup_btn.bind(on_release=self.create_backup)
        bottom.add_widget(backup_btn)

        refresh_btn = Button(text="Atualizar lista")
        refresh_btn.bind(on_release=lambda *_: self.populate_tree())
        bottom.add_widget(refresh_btn)
        root.add_widget(bottom)

        return root

    def popup(self, title, message):
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint_y=None, height=dp(45))
        content.add_widget(btn)
        pop = Popup(title=title, content=content, size_hint=(.9, .45))
        btn.bind(on_release=pop.dismiss)
        pop.open()

    def open_file(self, *_):
        # Android: usa o seletor de arquivos do sistema quando disponível.
        try:
            from plyer import filechooser

            filechooser.open_file(
                filters=["*.dbi", "*.bin", "*.img", "*.iso", "*.*"],
                on_selection=self.file_selected,
            )
        except Exception as e:
            self.popup(
                "Abrir arquivo",
                "O seletor de arquivos não pôde ser aberto.\n"
                "Instale plyer e conceda permissão de acesso aos arquivos.\n\n"
                + str(e),
            )

    def file_selected(self, selection):
        if not selection:
            return
        path = selection[0]
        self.load_file(path)

    def load_file(self, path):
        try:
            self.bin_path = path
            self.read_database(path)
            self.populate_tree()

            filename = os.path.basename(path)
            self.status.text = (
                f"🟢 {filename} | {len(self.player_records)} jogadores encontrados."
            )
        except Exception as e:
            self.popup("Erro de leitura", str(e))

    def read_database(self, file_path):
        self.player_records = []

        with open(file_path, "rb") as f:
            raw_data = f.read()

        HEX_INICIO = bytes.fromhex("00 44 61 76 69 64 FF 53")
        HEX_FIM = bytes.fromhex("4F 72 61 7A 65 00 CD CD")

        start_offset = raw_data.find(HEX_INICIO)

        if start_offset == -1:
            start_offset = raw_data.find(b"David\xffS") - 1

        if start_offset == -1:
            raise ValueError(
                "Assinatura do banco de jogadores não foi encontrada!"
            )

        end_offset = raw_data.find(HEX_FIM, start_offset)

        if end_offset != -1:
            end_offset += len(HEX_FIM)
        else:
            end_offset = start_offset + 140000

        i = start_offset + 1
        player_count = 0

        while i < min(end_offset - 2, len(raw_data)):
            if raw_data[i] == 0:
                i += 1
                continue

            str_start = i

            while i < end_offset and i < len(raw_data) and raw_data[i] != 0:
                i += 1

            block = raw_data[str_start:i]

            if b"\xff" in block:
                parts = block.split(b"\xff", 1)
                fn = parts[0].decode("latin-1", errors="replace") if parts[0] else ""
                ln = parts[1].decode("latin-1", errors="replace") if parts[1] else ""
            else:
                fn = ""
                try:
                    ln = block.decode("latin-1")
                except UnicodeDecodeError:
                    ln = ""

            if (len(fn) >= 2 or len(ln) >= 2) and len(block) >= 3:
                self.player_records.append(
                    {
                        "id": player_count + 1,
                        "start": str_start,
                        "length": len(block),
                        "first": fn,
                        "last": ln,
                        "has_ff": b"\xff" in block,
                    }
                )
                player_count += 1

            i += 1

    def populate_tree(self, indices=None):
        if indices is None:
            target = list(range(len(self.player_records)))
        else:
            target = list(indices)

        self.filtered_indices = target

        data = []
        for idx in target:
            rec = self.player_records[idx]
            data.append(
                {
                    "id": rec["id"],
                    "first": rec["first"],
                    "last": rec["last"],
                    "offset_hex": hex(rec["start"]),
                    "max_bytes": rec["length"],
                }
            )

        self.list.data = data

    def filter_players(self, *_):
        query = self.search.text.lower().strip()

        if not query:
            self.populate_tree()
            return

        matching = [
            i
            for i, r in enumerate(self.player_records)
            if query in r["first"].lower() or query in r["last"].lower()
        ]
        self.populate_tree(matching)

    def select_player_by_id(self, player_id):
        try:
            real_idx = int(player_id) - 1
            rec = self.player_records[real_idx]
        except (ValueError, IndexError):
            return

        self.selected_index = real_idx

        self.first_input.text = rec["first"]
        self.last_input.text = rec["last"]

        cur_bytes = (
            len(rec["first"].encode("latin-1", errors="replace"))
            + (1 if rec["has_ff"] else 0)
            + len(rec["last"].encode("latin-1", errors="replace"))
        )

        self.bytes_info.text = f"Bytes: {cur_bytes}/{rec['length']}"
        self.save_btn.disabled = False

    def create_backup(self, *_):
        if not self.bin_path:
            self.popup("Backup", "Abra primeiro um arquivo.")
            return

        try:
            src = Path(self.bin_path)
            backup = src.with_name(src.name + ".backup")
            shutil.copy2(src, backup)
            self.popup("Backup criado", f"Backup salvo como:\n{backup.name}")
        except Exception as e:
            self.popup("Erro no backup", str(e))

    def save_player_directly(self, *_):
        if self.selected_index is None or not self.bin_path:
            return

        rec = self.player_records[self.selected_index]

        new_fn = self.first_input.text.strip()
        new_ln = self.last_input.text.strip()

        try:
            fn_bytes = new_fn.encode("latin-1")
            ln_bytes = new_ln.encode("latin-1")
        except UnicodeEncodeError:
            self.popup(
                "Caracteres inválidos",
                "O formato original usa Latin-1. "
                "Use caracteres compatíveis com essa codificação.",
            )
            return

        if rec["has_ff"] or new_fn != "":
            block = fn_bytes + b"\xff" + ln_bytes
        else:
            block = ln_bytes

        if len(block) > rec["length"]:
            self.popup(
                "Limite excedido",
                f"O nome ocupa {len(block)} bytes, "
                f"mas o limite original é {rec['length']} bytes.",
            )
            return

        block += b"\x00" * (rec["length"] - len(block))

        try:
            with open(self.bin_path, "r+b") as f:
                f.seek(rec["start"])
                f.write(block)

            rec["first"] = new_fn
            rec["last"] = new_ln

            self.bytes_info.text = (
                f"Bytes: {len(block.rstrip(b'\\x00'))}/{rec['length']}"
            )

            self.populate_tree(self.filtered_indices)
            self.popup(
                "Salvo!",
                f"Jogador '{new_fn} {new_ln}' salvo com sucesso.",
            )
        except Exception as e:
            self.popup("Erro ao gravar", str(e))


if __name__ == "__main__":
    FIFA2001AndroidEditor().run()
