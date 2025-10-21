"use client";

import { useState } from "react";
import type { ProductResult, Retailer } from "./medicine-finder";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select";
import Image from "next/image";

type ResultsDisplayProps = {
  results: ProductResult[];
};

export function ResultsDisplay({ results }: ResultsDisplayProps) {
  const [sortBy, setSortBy] = useState<"price-low" | "price-high" | "rating">(
    "price-low"
  );
  const [filterAvailability, setFilterAvailability] = useState<string>("all");

  const sortRetailers = (retailers: Retailer[]) => {
    let sorted = [...retailers];

    // Filter by availability
    if (filterAvailability !== "all") {
      sorted = sorted.filter((r) => r.availability === filterAvailability);
    }

    // Sort
    switch (sortBy) {
      case "price-low":
        sorted.sort((a, b) => a.price - b.price);
        break;
      case "price-high":
        sorted.sort((a, b) => b.price - a.price);
        break;
      case "rating":
        sorted.sort((a, b) => (b.rating || 0) - (a.rating || 0));
        break;
    }

    return sorted;
  };

  return (
    <div className="space-y-6">
      {results.map((product) => (
        <Card
          key={product.id}
          className="overflow-hidden border-border/50 bg-card/80 shadow-xl backdrop-blur-sm"
        >
          <CardHeader className="pt-6 border-b border-border/50 bg-gradient-to-r from-primary/10 to-accent/10">
            <div className="flex items-start gap-4">
              {/* <div className="relative">
                <Image
                  src={product.image || "/placeholder.svg"}
                  alt={product.name}
                  width={80}
                  height={80}
                  className="rounded-xl border-2 border-primary/30 shadow-lg"
                />
                <div className="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-primary to-accent shadow-md">
                  <svg
                    className="h-3 w-3 text-primary-foreground"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
              </div> */}
              <div className="flex-1">
                <CardTitle className="text-lg text-foreground">
                  {product.name}
                </CardTitle>
                <CardDescription className="mt-1 text-muted-foreground">
                  {product.description}
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="pt-4">
            <div className="mb-4 flex flex-wrap items-center gap-3 rounded-lg border border-border/50 bg-muted/30 p-3">
              <div className="flex items-center gap-2">
                <svg
                  className="h-4 w-4 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
                  />
                </svg>
                <span className="text-sm font-medium text-foreground">
                  Sort:
                </span>
                <Select value={sortBy} onValueChange={(v: any) => setSortBy(v)}>
                  <SelectTrigger className="w-[150px] border-border/50 bg-card/80">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="price-low">
                      Price: Low to High
                    </SelectItem>
                    <SelectItem value="price-high">
                      Price: High to Low
                    </SelectItem>
                    <SelectItem value="rating">Highest Rated</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center gap-2">
                <svg
                  className="h-4 w-4 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
                  />
                </svg>
                <span className="text-sm font-medium text-foreground">
                  Filter:
                </span>
                <Select
                  value={filterAvailability}
                  onValueChange={setFilterAvailability}
                >
                  <SelectTrigger className="w-[140px] border-border/50 bg-card/80">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="in-stock">In Stock</SelectItem>
                    <SelectItem value="low-stock">Low Stock</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-3">
              {sortRetailers(product.retailers).map((retailer, index) => (
                <div
                  key={index}
                  className="group flex items-center justify-between rounded-xl border border-border/50 bg-gradient-to-r from-card/80 to-card/60 p-4 shadow-md backdrop-blur-sm transition-all hover:border-primary/50 hover:shadow-lg hover:shadow-primary/10"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                        <svg
                          className="h-5 w-5 text-primary"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
                          />
                        </svg>
                      </div>
                      <div>
                        <h4 className="font-semibold text-foreground">
                          {retailer.name}
                        </h4>
                        <Badge
                          variant={
                            retailer.availability === "in-stock"
                              ? "default"
                              : retailer.availability === "low-stock"
                              ? "secondary"
                              : "outline"
                          }
                          className="mt-1 text-xs"
                        >
                          {retailer.availability === "in-stock"
                            ? "✓ In Stock"
                            : retailer.availability === "low-stock"
                            ? "⚠ Low Stock"
                            : "✕ Out of Stock"}
                        </Badge>
                      </div>
                    </div>
                    <div className="mt-2 flex items-center gap-4 text-sm text-muted-foreground">
                      {retailer.rating && (
                        <span className="flex items-center gap-1">
                          <svg
                            className="h-4 w-4 fill-primary text-primary"
                            viewBox="0 0 20 20"
                          >
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                          <span className="font-medium text-foreground">
                            {retailer.rating}
                          </span>
                        </span>
                      )}
                      {retailer.shippingTime && (
                        <span className="flex items-center gap-1">
                          <svg
                            className="h-4 w-4 text-primary"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0"
                            />
                          </svg>
                          {retailer.shippingTime}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-2xl font-bold text-primary">
                        ${retailer.price.toFixed(2)}
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Best price
                      </p>
                    </div>
                    <Button
                      size="sm"
                      className="shrink-0 bg-gradient-to-br from-primary to-accent shadow-md shadow-primary/20 transition-all hover:shadow-lg hover:shadow-primary/30"
                    >
                      <svg
                        className="mr-1 h-4 w-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                        />
                      </svg>
                      View Deal
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
