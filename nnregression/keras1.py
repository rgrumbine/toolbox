import tensorflow as tf

#length = 33
#ratio = 5
  
fashion_mnist = tf.keras.datasets.fashion_mnist.load_data()
(x_train_full, y_train_full), (x_test, y_test) = fashion_mnist
x_train, y_train = x_train_full[:-5000], y_train_full[:-5000]
x_valid, y_valid = x_train_full[-5000:], y_train_full[-5000:]

print(x_train.shape, x_train.dtype)

x_train, x_valid, x_test = x_train/255., x_valid/255., x_test/255.
class_names = ['a','b','c','d','e','f','g','h','i','j']
print(class_names[y_train[0]])


tf.random.set_seed(42)
print("hello")
model = tf.keras.Sequential()
print("hello2")
model.add(tf.keras.layers.Input(shape=[28,28]))
print("hello3")
model.add(tf.keras.layers.Flatten() )
print("hello4",flush=True)
model.add(tf.keras.layers.Dense(300, activation="relu"))
print("hello5",flush=True)
model.add(tf.keras.layers.Dense(100, activation="relu"))
print("hello6",flush=True)
model.add(tf.keras.layers.Dense(10, activation="softmax"))
print("hello7",flush=True)

print(model.summary() )

model.compile(loss = 'sparse_categorical_crossentropy',
              optimizer='sgd',
              metrics=['accuracy'])

history = model.fit(x_train, y_train, epochs=30, validation_data=(x_valid, y_valid) )


