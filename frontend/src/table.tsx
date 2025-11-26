export const getStripeColoring = (index: number) => {
  return index % 2 === 0 ? "" : "bg-gray-100 dark:bg-gray-800";
}
