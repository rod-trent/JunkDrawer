# utils/generators.py
import json
import genanki
import plotly.graph_objects as go
import networkx as nx

# ===================== ANKI DECK GENERATOR =====================
def create_anki_deck(deck_name: str, flashcards: list) -> str:
    """
    Creates a real .apkg Anki deck from list of (front, back, extra) tuples.
    Returns the filename.
    """
    # Simple Anki model (front + back)
    my_model = genanki.Model(
        1607392319,
        'Simple Model',
        fields=[{'name': 'Front'}, {'name': 'Back'}],
        templates=[{
            'name': 'Card 1',
            'qfmt': '{{Front}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
        }],
        css='''
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        '''
    )

    # Create deck
    my_deck = genanki.Deck(
        deck_id=abs(hash(deck_name)) % (10 ** 10),
        name=deck_name
    )

    # Add notes
    for i, (front, back, extra) in enumerate(flashcards):
        if not front.strip() or not back.strip():
            continue
        note = genanki.Note(
            model=my_model,
            fields=[front.strip(), back.strip()]
        )
        my_deck.add_note(note)

    # Save to file
    filename = f"{deck_name.replace(' ', '_').replace('/', '-')}_Anki_Deck.apkg"
    genanki.Package(my_deck).write_to_file(filename)
    
    return filename


# ===================== MIND MAP GENERATOR =====================
def generate_mindmap(topic: str, data) -> go.Figure:
    """
    Robust mind map from Grok's JSON (handles strings, escaped with \\, truncated, etc.)
    """
    # Clean if it's a string
    if isinstance(data, str):
        cleaned = data.replace("\\", "")
        if cleaned.endswith(","):
            cleaned = cleaned[:-1]
        start = cleaned.find('{"title"')
        if start == -1:
            return None
        cleaned = cleaned[start:]
        try:
            data = json.loads(cleaned)
        except:
            return None

    # Ensure dict
    if isinstance(data, list):
        data = data[0] if data else {"title": topic, "children": []}
    if not isinstance(data, dict):
        return None

    # Build graph
    G = nx.DiGraph()
    def add_nodes(node, parent=None):
        title = node.get("title", "Unknown")
        G.add_node(title)
        if parent:
            G.add_edge(parent, title)
        for child in node.get("children", []):
            if isinstance(child, dict):
                add_nodes(child, title)

    add_nodes(data)

    if len(G.nodes) == 0:
        return None

    # Layout
    pos = nx.spring_layout(G, k=4, iterations=60, seed=42)

    # Edges
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    # Nodes
    node_x = [pos[n][0] for n in G.nodes()]
    node_y = [pos[n][1] for n in G.nodes()]
    node_text = list(G.nodes())

    fig = go.Figure()

    # Edges
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y,
                             line=dict(width=2, color="#888"),
                             hoverinfo='none',
                             mode='lines'))

    # Nodes
    fig.add_trace(go.Scatter(x=node_x, y=node_y,
                             mode='markers+text',
                             text=node_text,
                             textposition="middle center",
                             hoverinfo='text',
                             marker=dict(size=50, color="#4e79a7",
                                         line=dict(width=2, color="white"))))

    fig.update_layout(
        title=f"Mind Map: {topic}",
        titlefont_size=24,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=80),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white',
        height=800,
        paper_bgcolor='white'
    )

    return fig