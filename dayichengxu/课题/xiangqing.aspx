<%@ Page Title="" Language="C#" MasterPageFile="~/MasterPage.master" AutoEventWireup="true" CodeFile="xiangqing.aspx.cs" Inherits="xiangqing" %>

<asp:Content ID="Content1" ContentPlaceHolderID="head" Runat="Server">
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" Runat="Server">
    <div align="center" style="background-image: url('图片/0008020232552101_b.jpg')">
    
    <asp:GridView ID="GridView1" runat="server" AutoGenerateColumns="False" 
        Width="877px" Font-Size="25px" Height="285px">
        <Columns>
            <asp:ImageField DataImageUrlField="tupian">
            </asp:ImageField>
            <asp:BoundField DataField="xiangqing" HeaderText="参数" />
            <asp:BoundField DataField="xinghao" HeaderText="型号" />
            <asp:BoundField DataField="jiage" HeaderText="价格" />
        </Columns>
    </asp:GridView>
        <asp:Button ID="Button1" runat="server" Text="加入购物车" />
    </div>
</asp:Content>

