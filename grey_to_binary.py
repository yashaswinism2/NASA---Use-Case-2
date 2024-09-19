from PIL import Image
import numpy as np
import psycopg2

def image_to_binary(image_path):
    """Convert an image to binary data and return dimensions."""
    img = Image.open(image_path).convert('L') 
    img_array = np.array(img)  
    binary_data = (img_array > 127).astype(np.uint8) 
    return binary_data.flatten(), img.size  


def store_binary_data(binary_data, width, height, db_name='Solar_strom', user='postgres', password='root'):
    """Store binary data and dimensions in PostgreSQL database."""
    conn = psycopg2.connect(database=db_name, user=user, password=password)
    cursor = conn.cursor()
    
    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id SERIAL PRIMARY KEY,
            binary_data BYTEA NOT NULL,
            width INT NOT NULL,
            height INT NOT NULL
        )
    ''')
    
    print(f"Inserting data: width={width}, height={height}, binary_data_length={len(binary_data.tobytes())}")
    cursor.execute('INSERT INTO images (binary_data, width, height) VALUES (%s, %s, %s)', (binary_data.tobytes(), width, height))
    
    conn.commit()
    cursor.close()
    conn.close()


def retrieve_image(image_id, db_name='Solar_strom', user='postgres', password='root'):
    """Retrieve and display an image from the database."""
    conn = psycopg2.connect(database=db_name, user=user, password=password)
    cursor = conn.cursor()
    
    cursor.execute('SELECT binary_data, width, height FROM images WHERE id=%s', (image_id,))
    binary_data, width, height = cursor.fetchone()  # Fetch binary data and dimensions
    
    img_array = np.frombuffer(binary_data, dtype=np.uint8)
    img_array = img_array.reshape((height, width))  
    
    img = Image.fromarray(img_array * 255) 
    img.show()

    cursor.close()
    conn.close()


if __name__ == "__main__":
    image_path = '/Users/yashu/Downloads/grayscale_img.jpg'  
    binary_data, (width, height) = image_to_binary(image_path)
    
    store_binary_data(binary_data, width, height, db_name='Solar_strom', user='postgres', password='root')
    retrieve_image(image_id=2, db_name='Solar_strom', user='postgres', password='root')
