CREATE TABLE IF NOT EXISTS public.listing_price_history (
    id SERIAL PRIMARY KEY,
    listing_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_date TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (listing_id) REFERENCES public.listing(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_listing_id ON public.listing_price_history(listing_id);

INSERT INTO public.listing_price_history (listing_id, price, created_date)
SELECT id, price, NOW()
FROM public.listing;
