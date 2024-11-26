import certgen_py;

class ImageBlock:
    def __init__(self, path, dpi, pos):
        self.path = path
        self.dpi = dpi
        self.pos = pos

class TextNode:
    def __init__(self, content, font_size, line_height):
        self.content = content
        self.font_size = font_size
        self.line_height = line_height

class TextBlock:
    def __init__(self, nodes, pos):
        self.nodes = nodes
        self.pos = pos

# Artefacts cast with placeholder content
blocks = [
    # ImageBlock(path='logo.jpg', dpi=75.0, pos=(200.0, 14.0)),
    # ImageBlock(path='asset.jpg', dpi=240.0, pos=(195.0, 80.0)),
    # ImageBlock(path='signature.jpg', dpi=100.0, pos=(70.0, 220.0)),
    TextBlock(nodes=[
        TextNode(content="Placeholder Company Name", font_size=30.0, line_height=18.0),
        TextNode(content="Replublica Argentina y Juan Jose Castelli\nRincon de los Sauces", font_size=14.0, line_height=18.0),
    ], pos=(20.0, 24.0)),
    TextBlock(nodes=[
        TextNode(content="Certificado de Inspeccion", font_size=38.0, line_height=18.0),
    ], pos=(20.0, 58.0)),
    TextBlock(nodes=[
        TextNode(content="Numero de Certificado", font_size=14.0, line_height=18.0),
        TextNode(content="Placeholder Certificate ID", font_size=16.0, line_height=18.0),
        TextNode(content="\nFecha de Vencimiento", font_size=14.0, line_height=18.0),
        TextNode(content="Placeholder Expiration Date", font_size=22.0, line_height=18.0),
        TextNode(content="\nTipo de Ensayo Realizado", font_size=14.0, line_height=18.0),
        TextNode(content="Placeholder Test Type", font_size=16.0, line_height=18.0),
        TextNode(content="\nIdenticacion de la pieza", font_size=14.0, line_height=18.0),
        TextNode(content="Placeholder Asset ID", font_size=16.0, line_height=18.0),
        TextNode(content="\nTipo de pieza", font_size=14.0, line_height=18.0),
        TextNode(content="Placeholder Asset Type", font_size=16.0, line_height=18.0),
        TextNode(content="\nResultado", font_size=14.0, line_height=18.0),
        TextNode(content="Aprobado", font_size=22.0, line_height=18.0),
        TextNode(content="\nResponsable de la certication", font_size=14.0, line_height=18.0),
        TextNode(content="Juan Herrero", font_size=16.0, line_height=18.0),
    ], pos=(20.0, 80.0)),
]

certgen_py.gen_pdf(
    path="output.pdf",
    width=215.9,
    height=279.4,
    blocks=blocks
)

