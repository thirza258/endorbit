export interface Product {
  product_url: string;
  product_name: string;
  retail_price: number;
  image: string;
  description: string;
  product_rating: number | null;
  brand: string;
}

export interface ApiResponse {
  status: number;
  message: string;
  data: {
    response: string;
    products?: Product[];
  };
}
