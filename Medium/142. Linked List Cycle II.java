
/*Given the head of a linked list, return the node where the cycle begins. If there is no cycle, return null.

There is a cycle in a linked list if there is some node in the list that can be reached again by continuously following the next pointer.
Internally, pos is used to denote the index of the node that tail's next pointer is connected to (0-indexed).
It is -1 if there is no cycle. Note that pos is not passed as a parameter.

Do not modify the linked list
 */
  class ListNode {
      int val;
      ListNode next;
      ListNode(int x) {
         val = x;
         next = null;
      }
 }

class Solution {
      public ListNode intersection(ListNode head){
          ListNode slow = head;
          ListNode fast = head;
          while(fast != null && fast.next != null){
              slow = slow.next;
              fast = fast.next.next;
              if (slow == fast) {
                  return slow;
              }

          }
          return null;
      }
    public ListNode detectCycle(ListNode head) {
 if (head == null || head.next == null) {
     return null;
 }
 ListNode intersect = intersection(head);
 if (intersect == null) {
     return null;
 }
    ListNode start = head;
    while (intersect !=start){
        start = start.next;
        intersect = intersect.next;
    }
    return start;
    }
}

 public class Main {
     public static void main(String[] args) {

         Solution solution = new Solution();

         ListNode node1 = new ListNode(1);
         ListNode node2 = new ListNode(2);
         ListNode node3 = new ListNode(3);
         ListNode node4 = new ListNode(4);
         ListNode node5 = new ListNode(5);
         node1.next = node2;
         node2.next = node3;
         node3.next = node4;
         node4.next = node5;
         node5.next = node2;
         ListNode result = solution.detectCycle(node1);
         System.out.println("Cycle start " + result.val);

     }
 }