#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import pandas as pd


# In[35]:


def load_json(filename):
    with open(filename, encoding='ISO-8859-1') as f:
        data = json.load(f, encoding='latin1')
    return data

def is_interesting(product):
    return len(product['oferta']) and product['disponibilidade'] and not product['is_marketplace']

def get_interesting(data):
    interesting = []
    for page in range(len(data)):
        for product in data[page]:
            if is_interesting(product):
                name = product['nome']
                full_price = max(product['preco_antigo'], product['preco'])
                offer_price = product['preco_desconto']
                discount_percent = round(100.0 * (full_price - offer_price) / full_price)
                amount = product['oferta']['quantidade']
                product_url = 'https://www.kabum.com.br' + product['link_descricao']
                interesting.append(
                    [name, 
                     full_price, 
                     offer_price, 
                     discount_percent,
                     amount,
                     product_url])
                
    return interesting


# In[36]:


data = load_json('results.json')


# In[37]:


df = pd.DataFrame(data=get_interesting(data), columns=['nome', 
                                                       'precoTotal',
                                                       'precoBom',
                                                       'desconto',
                                                       'quantidade',
                                                       'URL'])


# In[38]:


sorted_df = df.sort_values(by='desconto', ascending=False)
sorted_df.to_csv('melhores_descontos.csv', index=False)


# In[ ]:




