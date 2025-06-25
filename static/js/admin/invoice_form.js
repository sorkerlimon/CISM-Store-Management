(function($) {
    $(document).ready(function() {
        // Get references to the customer and order dropdowns
        const customerSelect = $('#id_customer');
        const orderSelect = $('#id_order');
        
        // Function to update order dropdown based on selected customer
        function updateOrderDropdown() {
            const customerId = customerSelect.val();
            
            // Clear current options
            orderSelect.empty().append($('<option></option>').attr('value', '').text('---------'));
            
            // If no customer selected, don't fetch orders
            if (!customerId) {
                return;
            }
            
            // Fetch orders for the selected customer
            $.ajax({
                url: '/admin/ajax/orders-by-customer/',
                data: { 'customer_id': customerId },
                dataType: 'json',
                success: function(data) {
                    // Add each order to the dropdown
                    $.each(data.orders, function(i, order) {
                        orderSelect.append(
                            $('<option></option>')
                                .attr('value', order.id)
                                .text(order.display_text)
                        );
                    });
                }
            });
        }
        
        // Update orders when customer changes
        customerSelect.on('change', updateOrderDropdown);
        
        // Initialize on page load
        updateOrderDropdown();
    });
})(django.jQuery); 