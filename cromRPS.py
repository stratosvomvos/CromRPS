import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
from html.parser import HTMLParser
from urllib.parse import quote


class SimpleHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements, self.tag_stack = [], []
        self.current_a = None
        self.ignored = {"option", "select", "script", "style"}

    def handle_starttag(self, tag, attrs):
        if tag in self.ignored:
            self.tag_stack.append(tag)
            return
        self.elements.append(("start", tag, dict(attrs)))
        self.tag_stack.append(tag)
        if tag == "a":
            self.current_a = dict(attrs).get("href", "#")

    def handle_data(self, data):
        if not self.tag_stack or self.tag_stack[-1] in self.ignored:
            return
        text = data.strip()
        if text:
            self.elements.append(("text", "a" if self.tag_stack[-1] == "a" else self.tag_stack[-1], (text, self.current_a) if self.tag_stack[-1] == "a" else text))

    def handle_endtag(self, tag):
        if tag in self.ignored:
            self.tag_stack.pop()
            return
        self.elements.append(("end", tag))
        if self.tag_stack:
            self.tag_stack.pop()
            if tag == "a":
                self.current_a = None


class HTMLRenderer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CromRPS")
        self.geometry("800x600")
        self.current_url = ""

        self.top = tk.Frame(self)
        self.top.pack(fill=tk.X)

        self.url_box = tk.Entry(self.top, width=50) 
        self.url_box.pack(side=tk.LEFT, padx=10, pady=5)

        self.go_btn = tk.Button(self.top, text="Go", command=self.load_page)
        self.go_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.txt = scrolledtext.ScrolledText(self, wrap=tk.WORD, state=tk.NORMAL, font=("Arial", 12))
        self.txt.pack(fill=tk.BOTH, expand=True)
        self.txt.bind("<Key>", lambda e: "break")

        self.menu_setup()

    def menu_setup(self):
        bar = tk.Menu(self)
        file = tk.Menu(bar, tearoff=0)
        file.add_command(label="Open URL", command=self.focus_url_box) 
        file.add_command(label="Reload", command=self.reload_page)
        file.add_separator()
        file.add_command(label="Exit", command=self.quit)
        bar.add_cascade(label="File", menu=file)
        help_menu = tk.Menu(bar, tearoff=0)
        help_menu.add_command(label="About", command=self.about_box)
        bar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=bar)

    def focus_url_box(self):
        self.url_box.focus_set()



    def reload_page(self):
        if self.current_url:
            self.load_page(url=self.current_url)
        else:
            messagebox.showinfo("Reload", "No page to reload, all hope is gone.")

    def load_page(self, url=None):
        self.current_url = url if url else self.url_box.get().strip()
        if not self.current_url:
            messagebox.showerror("Error", "lol")
            return

        if " " in self.current_url or "." not in self.current_url:
            self.current_url = f"https://duckduckgo.com/lite/?q={quote(self.current_url)}"
        elif not self.current_url.startswith(("http://", "https://")):
            self.current_url = "http://" + self.current_url

        self.url_box.delete(0, tk.END)
        self.url_box.insert(0, self.current_url)

        self.go_btn.config(text="Loading...")
        self.update_idletasks()

        try:
            res = requests.get(self.current_url, headers={"User-Agent": "Mozilla/5.0", "Cookie": "cookieconsent_status=allow"})
            if res.status_code == 200:
                print(f"Fetching page content for URL: {self.current_url}\nHTML content fetched successfully")
                self.render(res.text)
            else:
                messagebox.showerror("Error", f"Failed to fetch URL: {res.status_code}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

        self.go_btn.config(text="Go")

    def render(self, html):
        self.txt.config(state=tk.NORMAL)
        self.txt.delete("1.0", tk.END)
        link_count = 0

        p = SimpleHTMLParser()
        p.feed(html)
        for e in p.elements:
            if e[0] == "text":
                if e[1] == "a":
                    txt, href = e[2]
                    if txt:
                        tag = f"link_{link_count}"
                        self.txt.insert(tk.END, txt, tag)
                        self.txt.insert(tk.END, "\n")
                        self.txt.tag_config(tag, foreground="blue", underline=1)
                        self.txt.tag_bind(tag, "<Button-1>", lambda e, u=href: self.load_link(u))
                        link_count += 1
                else:
                    self.txt.insert(tk.END, e[2] + "\n")
        self.txt.config(state=tk.DISABLED)
        print("shown!")

    def load_link(self, url):
        self.url_box.delete(0, tk.END)
        self.url_box.insert(0, url)
        self.load_page()

    def about_box(self):
        messagebox.showinfo("About", "CromRPS \nAn extremely barebones web browser using a simple html renderer by me. Uses a custom user agent for certain websites to display. \nNot intended for anything else than Wikipedia or similar stuff lmao")


if __name__ == "__main__":
    HTMLRenderer().mainloop()
