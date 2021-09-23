import argparse
import numpy as np
import torch
from datetime import datetime, timezone

from gradient_check import eval_numerical_gradient, eval_numerical_gradient_array
from transformer_layers import *
from captioning_solver_transformer import CaptioningSolverTransformer
from transformer import CaptioningTransformer
from coco_utils import load_coco_data, sample_coco_minibatch, decode_captions

parser = argparse.ArgumentParser()
parser.add_argument("--base-dir", type=str, help="set dataset base directory")
parser.add_argument("--seed", type=int, default=333, help="seed")
parser.add_argument("--num-heads", type=int, default=2, help="number of attention heads")
parser.add_argument("--num-layers", type=int, default=2, help="number of transformer layers")
parser.add_argument("--wordvec-dim", type=int, default=256, help="Dimension W of word vectors")
parser.add_argument("--lr", type=float, default=0.001, help="learning rate of optimizer")
parser.add_argument("--tracking", action="store_true", help="use mlflow tracking")
parser.add_argument("--max-train", type=int, default=50, help="number of subset of trainset")
parser.add_argument("--epochs", type=int, default=100, help="number of training epochs")
parser.add_argument("--batch-size", type=int, default=25, help="number of batch size")
parser.add_argument("--max-length", type=int, default=30, help="max sequenth length")
parser.add_argument("--print-every", type=int, default=10, help="print every {} step") 
args = parser.parse_args()

if __name__ == "__main__":
    # fix random seed 
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    np.random.seed(args.seed)

    # Load COCO data from disk into a dictionary.
    data = load_coco_data(base_dir=args.base_dir, max_train=args.max_train, pca_features=True)

    # Print out all the keys and values from the data dictionary.

    for k, v in data.items():
        if type(v) == np.ndarray:
            print(k, type(v), v.shape, v.dtype)
        else:
            print(k, type(v), len(v))

    transformer = CaptioningTransformer(
          word_to_idx=data['word_to_idx'],
          input_dim=data['train_features'].shape[1],
          wordvec_dim=args.wordvec_dim,
          num_heads=args.num_heads,
          num_layers=args.num_layers,
          max_length=args.max_length
        )

    transformer_solver = CaptioningSolverTransformer(transformer, data, idx_to_word=data['idx_to_word'],
            num_epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.lr,
            verbose=True,
            print_every=args.print_every,
            tracking=args.tracking
            )

    transformer_solver.train(vars(args))

    print('Final loss: ', transformer_solver.loss_history[-1])
