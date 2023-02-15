import java.io.Serial;

class Solution {
    public int maxProfit(int[] prices) {
        int max_profit = 0;
        int min_price = Integer.MAX_VALUE;

        for(int i =0; i < prices.length;i++){
            if( min_price > prices[i] ){
                min_price = prices[i];
            }
            if( prices[i] - min_price > max_profit ){
                max_profit = prices[i] - min_price;
            }
        }
        return max_profit;
    }
}

 public class Main {
     public static void main(String[] args) {
         Solution solution = new Solution();
         int TEST [] = {7,1,5,3,6,4};
         int max_profit = solution.maxProfit(TEST);
         System.out.println(max_profit);
     }
 }