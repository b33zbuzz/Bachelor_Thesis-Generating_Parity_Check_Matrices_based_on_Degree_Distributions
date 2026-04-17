clear all
data = h5read("data.hdf5",'/dataset_01');
data = transpose(data);
data = double(data);
data = sparse(data);
save("H1024.mat","data");