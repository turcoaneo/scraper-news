import torch
import torch.nn as nn


class DeclensionModel(nn.Module):
    def __init__(self, vocab_size, hidden_dim, max_seq_len):
        super().__init__()
        self.encoder = nn.Embedding(vocab_size, hidden_dim)
        self.positional = nn.Embedding(max_seq_len, hidden_dim)
        self.decoder = nn.GRU(hidden_dim, hidden_dim, batch_first=True)
        self.output = nn.Linear(hidden_dim, vocab_size)

    def forward(self, input_ids):
        batch_size, seq_len = input_ids.size()
        device = input_ids.device

        # Create position indices safely
        positions = torch.arange(seq_len, dtype=torch.long, device=device).unsqueeze(0).expand(batch_size, seq_len)

        x = self.encoder(input_ids) + self.positional(positions)
        x, _ = self.decoder(x)
        return self.output(x)
