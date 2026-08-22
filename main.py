import os
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

KV = """
BoxLayout:
    orientation: "vertical"
    padding: 8
    spacing: 6

    BoxLayout:
        size_hint_y: None
        height: "48dp"
        Button:
            text: "Abrir arquivo"
            on_release: app.open_file_popup()
        Label:
            text: app.status
            text_size: self.size
            valign: "middle"

    TextInput:
        id: search
        hint_text: "Buscar jogador"
        size_hint_y: None
        height: "42dp"
        multiline: False
        on_text: app.filter_players(self.text)

    RecycleView:
        id: rv
        viewclass: "Row"
        RecycleBoxLayout:
            default_size: None, "40dp"
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: "vertical"

    BoxLayout:
        size_hint_y: None
        height: "48dp"
        TextInput:
            id: first
            hint_text: "Nome"
            multiline: False
        TextInput:
            id: last
            hint_text: "Sobrenome"
            multiline: False
        Button:
            text: "Salvar"
            size_hint_x: .3
            on_release: app.save_player()

<Row@Button>:
    text: root.text
    on_release: app.select_player(root.index)
"""

class FIFAEditorApp(App):
    status = StringProperty("Nenhum arquivo aberto")
    player_records = ListProperty([])
    filtered_indices = ListProperty([])
    selected_index = NumericProperty(-1)
    bin_path = None

    def build(self):
        return Builder.load_string(KV)

    def popup_msg(self, title, msg):
        Popup(title=title, content=Label(text=msg), size_hint=(.8,.4)).open()

    def open_file_popup(self):
        chooser = FileChooserListView(filters=["*.dbi","*.bin","*.img","*.iso"])
        box = BoxLayout(orientation="vertical")
        box.add_widget(chooser)
        btn = __import__('kivy.uix.button', fromlist=['Button']).Button(text="Abrir", size_hint_y=None, height="48dp")
        box.add_widget(btn)
        pop = Popup(title="Selecionar arquivo", content=box, size_hint=(.95,.95))
        def choose(*args):
            if chooser.selection:
                pop.dismiss()
                self.load_file(chooser.selection[0])
        btn.bind(on_release=choose)
        pop.open()

    def load_file(self, path):
        try:
            self.bin_path = path
            self.read_database(path)
            self.populate_list()
            self.status = f"{os.path.basename(path)} | {len(self.player_records)} jogadores"
        except Exception as e:
            self.popup_msg("Erro", str(e))

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
            raise Exception("Assinatura do banco de jogadores não encontrada")

        end_offset = raw_data.find(HEX_FIM, start_offset)
        if end_offset != -1:
            end_offset += len(HEX_FIM)
        else:
            end_offset = start_offset + 140000

        i = start_offset + 1
        player_count = 0
        while i < end_offset - 2:
            if raw_data[i] == 0:
                i += 1
                continue
            str_start = i
            while i < end_offset and raw_data[i] != 0:
                i += 1
            block = raw_data[str_start:i]
            if b"\xff" in block:
                parts = block.split(b"\xff",1)
                fn = parts[0].decode("latin-1") if parts[0] else ""
                ln = parts[1].decode("latin-1") if parts[1] else ""
            else:
                fn = ""
                try:
                    ln = block.decode("latin-1")
                except:
                    ln = ""
            if (len(fn) >= 2 or len(ln) >= 2) and len(block) >= 3:
                self.player_records.append({"id":player_count+1,"start":str_start,"length":len(block),"first":fn,"last":ln,"has_ff":b"\xff" in block})
                player_count += 1
            i += 1

    def populate_list(self, indices=None):
        if indices is None:
            indices = range(len(self.player_records))
        self.filtered_indices = list(indices)
        self.root.ids.rv.data = [{"text": f"{self.player_records[i]['first']} {self.player_records[i]['last']}", "index": i} for i in self.filtered_indices]

    def filter_players(self, query):
        q = query.lower().strip()
        if not q:
            self.populate_list()
        else:
            self.populate_list([i for i,r in enumerate(self.player_records) if q in r["first"].lower() or q in r["last"].lower()])

    def select_player(self, idx):
        self.selected_index = idx
        rec = self.player_records[idx]
        self.root.ids.first.text = rec["first"]
        self.root.ids.last.text = rec["last"]

    def save_player(self):
        if self.selected_index < 0 or not self.bin_path:
            return
        rec = self.player_records[self.selected_index]
        fn = self.root.ids.first.text.strip()
        ln = self.root.ids.last.text.strip()
        block = fn.encode("latin-1") + b"\xff" + ln.encode("latin-1") if rec["has_ff"] or fn else ln.encode("latin-1")
        if len(block) > rec["length"]:
            self.popup_msg("Erro", "Nome excede o limite original")
            return
        block += b"\x00" * (rec["length"] - len(block))
        with open(self.bin_path, "r+b") as f:
            f.seek(rec["start"])
            f.write(block)
        rec["first"], rec["last"] = fn, ln
        self.populate_list(self.filtered_indices)
        self.popup_msg("Salvo", "Jogador salvo com sucesso")

if __name__ == "__main__":
    FIFAEditorApp().run()
