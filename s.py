def merge(nums1, m, nums2, n):
    res = nums1[:m] + nums2
    return sorted(res)



print(merge([1,2,3,0,0,0], 3, [2,5,6], 3))
