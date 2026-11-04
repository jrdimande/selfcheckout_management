from django import forms


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            w = f.widget
            css = "form-select" if isinstance(w, forms.Select) else (
                "form-check-input" if isinstance(w, forms.CheckboxInput) else "form-control")
            w.attrs["class"] = (w.attrs.get("class", "") + " " + css).strip()


def date_field(label):
    return forms.DateField(required=False, label=label, widget=forms.DateInput(attrs={"type": "date"}))
