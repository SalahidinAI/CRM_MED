def rotate(nums, k):
    l = len(nums)
    print(nums[:l - k])
    print(nums[l - k:])
    nums[:l - k], nums[l - k:] = nums[l - k:], nums[:l - k]
    return nums


print(rotate([1,2,3,4,5,6,7], 3))
a = [1, 2, 3, 4]
a[:2], a[2:] = a[2:], a[:2]
print(a)
