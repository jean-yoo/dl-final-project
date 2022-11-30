from torch import nn
from transformers import Trainer, TrainingArguments, AutoFeatureExtractor, AutoTokenizer
from preprocess import dataset, MultimodalCollator, device, showImage, answer_space
from transformer_model import TransformerModel
from metrics import wups 

def create_trainer(model, train_dataset, eval_dataset, data_collator, metric):
    training_args = TrainingArguments(
        output_dir = '/Users/jean/Documents/CS1470/dl-final-project/transformer/transformer-checkpoints',
        seed = 1470,
        save_strategy = 'epoch',
        evaluation_strategy = 'epoch',
        logging_strategy = 'epoch',
        metric_for_best_model = 'wups',
        removed_unused_columns = False,
        num_train_epochs = 10,
        load_best_model_at_end = True, 
        fp16 = True, # allows for faster training of larger models and minibatch sizes 
        dataloader_num_workers = 2 # speed up data transfer between cpu and gpu 
        )
    trainer = Trainer(model, training_args, train_dataset, eval_dataset, data_collator, compute_metrics = metric)
    return trainer 
    

def train_model(): 
    # initialize tokenizer, feature extractor and pass into multimodal collator 
    text_tokenizer = AutoTokenizer.from_pretrained('albert-base-v2')
    feature_extractor = AutoFeatureExtractor.from_pretrained('microsoft/swin-tiny-patch4-window7-224')
    # initialize components 
    collator = MultimodalCollator(text_tokenizer, feature_extractor)
    model = TransformerModel().to(device) # move model to gpu 
    trainer = create_trainer(model, dataset['train'], dataset['test'], collator, wups)
    # train 
    train_metrics = trainer.train() 
    # evaluate
    eval_metrics = trainer.evaluate() 

    return model, collator, train_metrics, eval_metrics 

def model_inference(model, collator):
    sample = collator(dataset['test'][2000:2010])
    img_feat = sample['img_features'].to(device)
    text_feat = sample['text_features'].to(device)
    labels = sample['labels'].to(device)
    # put in evaluation mode
    model.eval() 
    # forward pass
    output = model(img_features = img_feat, text_features = text_feat, labels = labels) 
    preds = output['logits'].argmax(axis = -1).cpu().numpy() 
    for i in range(2000, 2010):
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        showImage(i)
        print("Prediction:\t", answer_space[preds[i-2000]])
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$")

