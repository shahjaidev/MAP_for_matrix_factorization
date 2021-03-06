# -*- coding: utf-8 -*-
"""hw3_p3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TTlkXPA2oWOT2crNuzLnpr_UK4VZyXql
"""



import numpy as np

import matplotlib.pyplot as plt

import math

import scipy

from google.colab import drive
drive.mount('/content/gdrive')

f= open("/content/gdrive/My Drive/P3/Prob3_movies.txt", 'r')

movies_li=[]
for line in f:
  line= line[:-1]
  movies_li.append(line)

f.close()

#for line in movies:
  #line=line.strip("\n")

ratings_li = np.genfromtxt("/content/gdrive/My Drive/P3/Prob3_ratings.csv", delimiter=",")
test= np.genfromtxt("/content/gdrive/My Drive/P3/Prob3_ratings_test.csv", delimiter=",")



ratings_li

num_users= max(ratings_li[0])

num_movies= max(ratings_li[1])

#As the highest uid idx corresponds to the number of such entities in the database

num_users= int(num_users)
num_movies= int(num_movies)

num_users

num_movies

from collections import defaultdict

user_dict, movie_dict= defaultdict(list), defaultdict(list)



ratings_li=np.transpose(ratings_li)

ratings_dict= {}
def build_user_and_movie_dicts():
  for r in ratings_li:
    if r[0] in user_dict:
      user_dict[r[0]].append(r[1])

    if r[1] in movie_dict:
      movie_dict[r[1]].append(r[0])
    else:
      user_idx=r[0]
      movie_idx= r[1]
      actual_rating= r[2]
      ratings_dict[(user_idx, movie_idx)]= actual_rating

build_user_and_movie_dicts()

def initialise_umat():
  u_mat=[]

  for i in range(num_users):
    u_mat.append(np.random.multivariate_normal(mean=np.zeros(10), cov= np.identity(10), size=1)[0])
  u_mat= np.asarray(u_mat)
  return u_mat

def initialise_vmat():
  v_mat=[]

  for i in range(num_movies):
    v_mat.append( np.random.multivariate_normal(mean=np.zeros(10), cov= np.identity(10), size=1)[0] )
  v_mat= np.asarray(v_mat)
  return v_mat



from numpy.linalg import norm

def calc_objective(u_mat,v_mat):
  term_1=0
  for i in range(0, len(ratings_li)):
    idx_a= int(ratings_li[i][0]) -1 
    idx_b= int(ratings_li[i][1] ) -1 
    temp_term= ratings_li[i][2]- u_mat[idx_a].dot( v_mat[idx_b ] )
    term_1+= temp_term**2

  term_2=0
  for i in range(num_users):
    term_2+= norm(u_mat[i])**2

  
  term_3=0
  print(v_mat[i])
  for i in range(num_movies):
    term_3+= norm(v_mat[i])**2
 
  L_tot= (term_1+term_2 + term_3)/2
  print(L_tot)
  return (-1 * L_tot)

from numpy.linalg import inv

def update_user_location(idx, user_idx, v):

  rt_term= np.zeros(10)

  
  m= 0.25 * np.identity(10)
  for movie_idx in user_dict[idx+1]:
    movie= int(movie_idx)
    vvt= np.asarray( [v[movie-1]].transpose().dot(np.asarray([v[movie-1]] ))     )

    m+= vvt
    rating=review_dict[tuple([idx+1, movie])]
    d= rating*v[movie-1]
    rt_term+= d
    m= inv(m)
  res= m.dot(rt_term)
  return (res)

def update_object_location(idx, movie_idx, u_mat):
  rt_term= np.zeros(10)


  m= 0.25 * np.identity(10)

  for u in movie_dict[idx+1]:
    user_idx= int(u)
    uut= np.asarray( [u_mat[user_idx-1]].transpose().dot(np.asarray([u_mat[user_idx-1]] ))     )

    m+= uut
    rating= review_dict[tuple([user_idx, idx+1])]
    d= rating*u_mat[user_idx-1]
    rt_term += d
    m= inv(m)

  res= m.dot(rt_term)
  return (res)

#goes from i=1 to N1 (number of user locations), updating each row
 def update_u(u_mat,v_mat):
   for i in range(1, u_mat.shape[0] + 1):
     if i in user_dict.keys():
       u_mat[i-1]= update_user_location(i-1, u_mat[i-1], v_mat)
   return u_mat

def update_v(u_mat,v_mat):
     for i in range(1, v_mat.shape[0] + 1):
      if i in movie_dict.keys():
        v_mat[i-1]=update_object_location(i-1, v_mat[i-1], u_mat)
     return v_mat

num_of_iterations= 100

from scipy.spatial.distance import euclidean

def run_MAP_coor_ascent():
  u=initialise_umat()
  v=initialise_vmat()
  L_func_values=[]

  for i in range(num_of_iterations):
    u=update_u(u,v)
    v=update_v(u,v)
    L_func_values.append(calc_objective(u,v) )
  return u,v, L_func_values

def predict_ratings(data,u_mat,v_mat):
  preds=[]
  for i in range(len(data)):
    #print(data)
    u_idx=data[i][0]-1
    v_idx= data[i][1]-1
    u_vect= u_mat[int(u_idx)]
    v_vect= v_mat[int(v_idx)]

    m=u_vect.dot(v_vect)
    rating=np.random.normal(m,0.25,1)[0]

    preds.append( rating )                         
  return preds

from sklearn.metrics import mean_squared_error

from math import sqrt

def plot_helper(i, L_func_values):
  plt.plot(range(num_of_iterations),  L_func_values, label=i                     )
  #plt.show()

run_results_dict={}


def run():

  
  #Looping over 10 runs
  for i in range(1,11):
    u_mat, v_mat, L_func_values_by_iter_li= run_MAP_coor_ascent()

    plot_helper(i, L_func_values_by_iter_li)

    y_predicted= predict_ratings(test,u_mat, v_mat)
    data_rating_li= [ d[j][2] for j in range(len(data))  ]
    rmse_error = sqrt(mean_squared_error(data_rating_li, y_predicted))

    run_results_dict[i-1]["rmse"]= rmse_error
    run_results_dict[i-1]["max_objective"]= L_func_values_by_iter_li[-1]
    run_results_dict[i-1]["u"]= u_mat
    run_results_dict[i-1]["v"]= v_mat


  plt.show()

run()

print(run_results_dict)

def print_final_objective_and_RMSE(): #for all 10 runs

  for cur_run in range(1,11):
    print(cur_run)
    print("Root Mean Square Error")
    print(run_results_dict[cur_run]["rmse"])
    print("Final iteration objective value:")
    print(run_results_dict[cur_run]["max_objective"])


print_final_objective_and_RMSE()

#Run having highest objective value
highest_v_mat= None

movie_2_idx_dict= dict()
idx_2_movie_dict = dict()

print(movies_li)

def build_dicts():
  for i in range(len(movies_li)):
    movie_2_idx_dict[movies_li[i]]=i
    idx_2_movie_dict[i]= movies_li[i]

build_dicts()

print(movie_2_idx_dict)
print(idx_2_movie_dict)

def top_k_closest(k, name,v_mat):
  recs=[]
  associated_rec_distances=[]

  idx= movie_2_idx_dict[name]
  dists_idx_tuple_li= []
  vidx= v_mat[idx]

  for i in range(len(v_mat)):
    if i== idx:
      continue
    else:
      l2_distance= euclidean(vidx, v_mat[i] )
      dists_idx_tuple_li.append((l2_distance, v_mat[i]))
    
    dists_idx_tuple_li=sorted(dists_idx_tuple_li)


    for i in range(k):
      distance, idx= dists_idx_tuple_li[i][0], dists_idx_tuple_li[i][1]
      name= idx_2_movie_dict[idx]
      associated_rec_distances.append(distance)
    
    return recs, associated_rec_distances

def query(k, query_str):
  print(query_str)
  recs, dists= top_k_closest(k, query_str, highest_vmat)
  print("recommended movies:")
  print("Associated distances")
  print(dists)

a="Star Wars (1977)"
query(10, a)

query(10, "My Fair Lady (1964)")

query(10, "GoodFellas(1990)")

