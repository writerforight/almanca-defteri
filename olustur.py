#!/usr/bin/env python3
"""konular.md + oturumlar/*.md -> index.html (tek dosya, veri gömülü)."""
import json
import re
from pathlib import Path

KOK = Path(__file__).resolve().parent


def konulari_oku():
    bolumler, acik, bolum = [], [], None
    for satir in (KOK / "konular.md").read_text(encoding="utf-8").splitlines():
        if satir.startswith("## "):
            bolum = {"ad": satir[3:].strip(), "maddeler": []}
            if bolum["ad"] != "Açık işler":
                bolumler.append(bolum)
            continue
        if not satir.startswith("- ") or bolum is None:
            continue
        m = re.match(r"- \[( |x)\] (.*)", satir)
        if m:
            acik.append({"bitti": m.group(1) == "x", "metin": m.group(2)})
            continue
        parca = [p.strip() for p in satir[2:].split(" — ")]
        madde = {"konu": parca[0], "tarih": "", "tekrar": 1, "not": ""}
        if len(parca) > 1:
            madde["tarih"] = parca[1]
        if len(parca) > 2 and parca[2].isdigit():
            madde["tekrar"] = int(parca[2])
        if len(parca) > 3:
            madde["not"] = " — ".join(parca[3:])
        bolum["maddeler"].append(madde)
    return bolumler, acik


def oturumlari_oku():
    dosyalar = sorted((KOK / "oturumlar").glob("*.md"), reverse=True)
    return [{"tarih": d.stem, "md": d.read_text(encoding="utf-8")} for d in dosyalar]


def main():
    bolumler, acik = konulari_oku()
    veri = {"bolumler": bolumler, "acik": acik, "oturumlar": oturumlari_oku()}
    sablon = (KOK / "sablon.html").read_text(encoding="utf-8")
    json_metin = json.dumps(veri, ensure_ascii=False).replace("</", "<\\/")
    (KOK / "index.html").write_text(sablon.replace("/*VERI*/null", json_metin), encoding="utf-8")
    print(f"index.html: {sum(len(b['maddeler']) for b in bolumler)} konu, {len(veri['oturumlar'])} oturum")


if __name__ == "__main__":
    main()
