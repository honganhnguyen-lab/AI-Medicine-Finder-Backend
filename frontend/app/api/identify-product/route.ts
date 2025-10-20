import { generateObject } from "ai"
import { z } from "zod"

export const maxDuration = 30

const retailerSchema = z.object({
  name: z.string().describe("Name of the retailer (e.g., CVS Pharmacy, Walgreens, Amazon Pharmacy, Rite Aid)"),
  price: z.number().describe("Price in USD"),
  availability: z.enum(["in-stock", "low-stock", "out-of-stock"]),
  rating: z.number().min(0).max(5).optional().describe("Customer rating out of 5"),
  shippingTime: z.string().optional().describe('Estimated shipping time (e.g., "2-3 days", "Next day")'),
})

const productSchema = z.object({
  name: z.string().describe("Full product name including dosage/strength"),
  description: z.string().describe("Brief description of the product and its uses"),
  category: z.string().describe("Product category (e.g., pain-relief, vitamins, cold-flu, first-aid)"),
  activeIngredients: z.array(z.string()).optional().describe("Active ingredients if applicable"),
  retailers: z.array(retailerSchema).describe("List of retailers selling this product with pricing"),
})

const identificationResultSchema = z.object({
  products: z.array(productSchema).min(1).max(5).describe("List of identified products or alternatives"),
  confidence: z.enum(["high", "medium", "low"]).describe("Confidence level of the identification"),
  notes: z.string().optional().describe("Additional notes or warnings about the products"),
})

function getMockData(query: string) {
  const mockProducts = [
    {
      name: "Ibuprofen 200mg Tablets",
      description:
        "Fast-acting pain reliever and fever reducer. Effective for headaches, muscle aches, and minor arthritis pain.",
      category: "pain-relief",
      activeIngredients: ["Ibuprofen 200mg"],
      retailers: [
        { name: "CVS Pharmacy", price: 8.99, availability: "in-stock" as const, rating: 4.5, shippingTime: "2-3 days" },
        { name: "Walgreens", price: 9.49, availability: "in-stock" as const, rating: 4.3, shippingTime: "Next day" },
        {
          name: "Amazon Pharmacy",
          price: 7.99,
          availability: "in-stock" as const,
          rating: 4.7,
          shippingTime: "1-2 days",
        },
        { name: "Rite Aid", price: 9.99, availability: "low-stock" as const, rating: 4.2, shippingTime: "3-4 days" },
      ],
    },
    {
      name: "Acetaminophen 500mg Extra Strength",
      description:
        "Extra strength pain reliever and fever reducer. Gentle on stomach, suitable for those who can't take NSAIDs.",
      category: "pain-relief",
      activeIngredients: ["Acetaminophen 500mg"],
      retailers: [
        {
          name: "CVS Pharmacy",
          price: 10.99,
          availability: "in-stock" as const,
          rating: 4.6,
          shippingTime: "2-3 days",
        },
        { name: "Target", price: 9.99, availability: "in-stock" as const, rating: 4.4, shippingTime: "2-3 days" },
        { name: "Walmart", price: 8.49, availability: "in-stock" as const, rating: 4.5, shippingTime: "3-5 days" },
        {
          name: "Amazon Pharmacy",
          price: 9.29,
          availability: "in-stock" as const,
          rating: 4.8,
          shippingTime: "1-2 days",
        },
      ],
    },
    {
      name: "Naproxen Sodium 220mg",
      description:
        "Long-lasting pain relief for up to 12 hours. Effective for arthritis, back pain, and menstrual cramps.",
      category: "pain-relief",
      activeIngredients: ["Naproxen Sodium 220mg"],
      retailers: [
        { name: "Walgreens", price: 11.99, availability: "in-stock" as const, rating: 4.4, shippingTime: "Next day" },
        {
          name: "CVS Pharmacy",
          price: 12.49,
          availability: "in-stock" as const,
          rating: 4.3,
          shippingTime: "2-3 days",
        },
        { name: "Rite Aid", price: 11.49, availability: "in-stock" as const, rating: 4.1, shippingTime: "3-4 days" },
      ],
    },
  ]

  return {
    products: mockProducts,
    confidence: "medium" as const,
    notes:
      "Demo mode: Using sample data. Add a credit card to Vercel AI Gateway for real AI-powered product identification.",
  }
}

export async function POST(req: Request) {
  try {
    const { query, image } = await req.json()

    if (!query && !image) {
      return Response.json({ error: "Either query or image must be provided" }, { status: 400 })
    }

    try {
      // Build the message content
      const messageContent: any[] = []

      if (query) {
        messageContent.push({
          type: "text",
          text: `Identify the medicine or healthcare product based on this description: "${query}". 
          
          Provide 2-4 relevant products that match the description. For each product:
          - Include accurate product names with dosages
          - Provide helpful descriptions
          - List 3-5 major pharmacy retailers (CVS, Walgreens, Amazon Pharmacy, Rite Aid, Target, Walmart)
          - Generate realistic price ranges based on typical market prices
          - Vary availability and ratings to be realistic
          - Include estimated shipping times
          
          If the query is vague, provide popular options in that category.`,
        })
      }

      if (image) {
        messageContent.push({
          type: "image",
          image: image,
        })

        messageContent.push({
          type: "text",
          text: "Identify the medicine or healthcare product in this image. Provide the exact product if recognizable, or similar alternatives if not clear.",
        })
      }

      const { object } = await generateObject({
        model: "openai/gpt-5",
        schema: identificationResultSchema,
        messages: [
          {
            role: "user",
            content: messageContent,
          },
        ],
        maxOutputTokens: 3000,
      })

      return Response.json(object)
    } catch (aiError: any) {
      console.log("[v0] AI Gateway unavailable, using mock data:", aiError.message)
      return Response.json(getMockData(query || "medicine"))
    }
  } catch (error) {
    console.error("Error identifying product:", error)
    return Response.json({ error: "Failed to identify product" }, { status: 500 })
  }
}
