function createObjectWithParamsForOutlook() {
    let obj_to_return = Object()
    let block_number = $('#block_number').val()
    if (block_number == 'Консультация' || block_number == 'Продление') {
        if (block_number == "Консультация") { obj_to_return.text_block = 'консультацию' }
        else { obj_to_return.text_block = 'продление' }
    }
    else { obj_to_return.text_block = `блок ${block_number}` }
    obj_to_return.check_link = $('#link').val()
    return obj_to_return
}